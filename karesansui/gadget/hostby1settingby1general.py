# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
@authors: Hiroki Takayasu <hiroki@karesansui-project.info>
"""

import os
import web

from karesansui import KaresansuiGadgetException, KaresansuiDBException, \
    config, sheconf
from karesansui.lib.file.k2v import K2V
from karesansui.lib.rest import Rest, auth
from karesansui.lib.file.configfile import LighttpdPortConf,\
    LighttpdSslConf, LighttpdAccessConf
from karesansui.lib.const import LIGHTTPD_COMMAND_UPDATE_CONFIG,\
    LIGHTTPD_CONF_TEMP_DIR, LIGHTTPD_PORT_CONFIG,\
    LIGHTTPD_ACCESS_CONFIG, LIGHTTPD_SSL_CONFIG,\
    LIGHTTPD_DEFAULT_PORT, PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    PROXY_ENABLE, PROXY_DISABLE
from karesansui.lib.utils import get_no_overlap_list, is_param, is_empty, \
    uniq_filename
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, \
    CHECK_MIN, CHECK_MAX, CHECK_LENGTH, \
    CHECK_ONLYSPACE
from karesansui.db.access.machine import findbyhost1, findby1uniquekey, update,\
    findbyalluniquekey
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.model._2pysilhouette import Job, JobGroup
from pysilhouette.command import dict2command

def validates_server(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'uniqkey'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Unique Key'))
    else:
        check = checker.check_unique_key(
                    _('Unique Key'),
                    obj.input.uniqkey,
                    CHECK_EMPTY | CHECK_VALID
                    ) and check

    if not is_param(obj.input, 'port'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Port Number'))
    else:
        check = checker.check_number(
                        _('Port Number'),
                        obj.input.port,
                        CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                        PORT_MIN_NUMBER,
                        PORT_MAX_NUMBER,
                        ) and check

    if not is_param(obj.input, 'access'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Access Policy'))
    else:
        if obj.input.access == 'all':
            check = True and check

        elif obj.input.access == 'network':
            if not obj.input.has_key('network'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Permit access from same network'))
            else:
                check = checker.check_cidr(
                            _('Permit Access From Same Network'),
                            obj.input.network,
                            CHECK_EMPTY | CHECK_VALID
                            ) and check

        elif obj.input.access == 'ipaddress':
            if not obj.input.has_key('access_ipaddress'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Permit access from specified IP address'))
            else:
                obj.input.ip_list = obj.input.access_ipaddress.split()
                obj.input.ip_list = get_no_overlap_list(obj.input.ip_list)
                if len(obj.input.ip_list) == 0:
                    check = False
                    checker.add_error(_('"%s" is required.') % _('IP Address'))
                for input_ip in obj.input.ip_list:
                    check = checker.check_ipaddr(
                                    _('Permit specified IP address'),
                                    input_ip,
                                    CHECK_EMPTY | CHECK_VALID
                                    ) and check

        else:
            check = False

    if not is_param(obj.input, 'ssl_status'):
        check = False
        checker.add_error(_('"%s" is required.') % _('SSL Settings'))
    else:
        if obj.input.ssl_status == 'enable':
            check = True and check
        elif obj.input.ssl_status == 'disable':
            check = True and check
        else:
            check = False

    obj.view.alert = checker.errors

    return check

def get_view_server_conf(config):
    try:
        conf_file = config['lighttpd.etc.dir'] + '/' + LIGHTTPD_PORT_CONFIG
        port_conf = LighttpdPortConf(conf_file)
        port_number = port_conf.read()

        conf_file = config['lighttpd.etc.dir'] + '/' + LIGHTTPD_ACCESS_CONFIG
        access_conf = LighttpdAccessConf(conf_file)
        access_list = access_conf.read()

        conf_file = config['lighttpd.etc.dir'] + '/' + LIGHTTPD_SSL_CONFIG
        ssl_conf = LighttpdSslConf(conf_file)
        ssl_status = ssl_conf.read()

    except IOError:
        raise KaresansuiGadgetException('Failed to read configuration file. - %s' %\
            conf_file)

    uniqkey = config['application.uniqkey']

    server_config = {
		     'uniqkey' : uniqkey,
                     'port' : port_number, 
                     'access' : access_list,
                     'ssl_status' : ssl_status,
                    }

    return server_config

def set_server_conf(config, input, session):
    if os.path.exists(LIGHTTPD_CONF_TEMP_DIR) is False:
        os.mkdir(LIGHTTPD_CONF_TEMP_DIR)

    tmp_file_names = {}

    # port.conf
    try:
        port_conf_path = LIGHTTPD_CONF_TEMP_DIR + '/kss_port_' + uniq_filename()
        port_conf = LighttpdPortConf(port_conf_path)
        port_conf.write(input)
        tmp_file_names['port'] = port_conf_path
    except AttributeError:
        raise KaresansuiGadgetException(
            'Failed to write configuration value input.port=%s at %s' % \
            (input.port, port_conf_path))

    # access.conf
    try:
        access_conf_path = LIGHTTPD_CONF_TEMP_DIR + '/kss_access_' + uniq_filename()
        access_conf = LighttpdAccessConf(access_conf_path)
        access_conf.write(input)
        tmp_file_names['access'] = access_conf_path
    except AttributeError:
        raise KaresansuiGadgetException(
            'Failed to write configuration value input.access=%s, input.access_ipaddress=%s, input.ip_list=%s at %s' % \
            (input.access, input.network, input.access_ipaddress, access_conf_path))

    # ssl.conf
    try:
        ssl_conf_path = LIGHTTPD_CONF_TEMP_DIR + '/kss_ssl_' + uniq_filename()
        ssl_conf = LighttpdSslConf(ssl_conf_path)
        ssl_conf.write(input)
        tmp_file_names['ssl'] = ssl_conf_path
    except AttributeError:
        raise KaresansuiGadgetException(
            'Failed to write configuration value input.ssl_status=%s at %s' % \
            (input.ssl_status, ssl_conf_path))

    config['application.uniqkey'] = input.uniqkey

    # check temporary files
    for key in ('port', 'access', 'ssl'):
        if not tmp_file_names.has_key(key):
            raise KaresansuiGadgetException(
				'Failed to make temporary file for %s' , key)
	elif os.path.isfile(tmp_file_names[key]) is False:
			raise KaresansuiGadgetException(
				'Not exist temporary file for %s' , key)

    return tmp_file_names

class HostBy1SettingBy1General(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            self.view.config = get_view_server_conf(config)
            return True
        except (IOError, KaresansuiGadgetException), kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_server(self):
            self.logger.debug("Update server setting failed. Did not validate.")
            return web.badrequest(self.view.alert)

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            tmp_unique_key = config['application.uniqkey']

            # make whether unique key is unique
            uniq_key_check = findbyalluniquekey(self.orm, self.input.uniqkey)
            if uniq_key_check != [] and config['application.uniqkey'] != self.input.uniqkey:
                self.logger.debug(
                    "Update unique key failed, Already exists Unique key - %s" % \
                    uniq_key_check[0].id)
                return web.conflict(web.ctx.path)

            lighttpdconf_path = set_server_conf(config, self.input, self.orm)

            _K2V.write(config)
        except (IOError, KaresansuiGadgetException), kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge

        # unique key
        try:
            host = findby1uniquekey(self.orm, tmp_unique_key)
            host.uniq_key = self.input.uniqkey
            update(self.orm, host)
        except KaresansuiDBException:
            # rollback
            config['application.uniqkey'] = tmp_unique_key
            _K2V.write(config)
            raise KaresansuiDBException

        # regist job
        cmdname = u"Update lighttpd config"
        options = {
                   'dest': config['lighttpd.etc.dir'],
                   'port': lighttpdconf_path['port'],
                   'ssl': lighttpdconf_path['ssl'],
                   'access': lighttpdconf_path['access']
                  }
        action_cmd = dict2command(
            "%s/%s" % (config['application.bin.dir'], LIGHTTPD_COMMAND_UPDATE_CONFIG),
            options)

        _jobgroup = JobGroup(cmdname, sheconf['env.uniqkey'])
        _job = Job('%s command' % cmdname, 0, action_cmd)
        _jobgroup.jobs.append(_job)

        host = findbyhost1(self.orm, 1);

        _machine2jobgroup = m2j_new(machine=host,
                            jobgroup_id=-1,
                            uniq_key=sheconf['env.uniqkey'],
                            created_user=self.me,
                            modified_user=self.me,
                            )

        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               _jobgroup
                               )

        self.view.config = get_view_server_conf(config)

        return web.accepted(url=web.ctx.path)

urls = ('/host/(\d+)/setting/general?(\.input|\.part)$', HostBy1SettingBy1General,)
