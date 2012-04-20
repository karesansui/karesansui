# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2012 HDE, Inc.
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

import web
import string
import re

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.db.model._2pysilhouette import Job, JobGroup, JOBGROUP_TYPE
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import jg_findby1, jg_save, corp
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from pysilhouette.command import dict2command

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.utils import is_param, generate_phrase, create_file, \
    get_filelist, symlink2real
from karesansui.lib.const import ISCSI_COMMAND_GET, ISCSI_COMMAND_UPDATE, \
    ISCSI_COMMAND_DELETE,     ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, \
    PORT_MIN_NUMBER,          PORT_MAX_NUMBER, \
    CHAP_USER_MIN_LENGTH,     CHAP_USER_MAX_LENGTH, \
    CHAP_PASSWORD_MIN_LENGTH, CHAP_PASSWORD_MAX_LENGTH, \
    ISCSI_DEVICE_DIR,         ISCSI_DEVICE_NAME_TPL, \
    VIRT_COMMAND_DESTROY_STORAGE_POOL, VIRT_COMMAND_DELETE_STORAGE_POOL

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_MIN, CHECK_MAX

def validates_network_storage(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'network_storage_host_name'):
        check = checker.check_domainname(_('Target Hostname'),
                                         obj.input.network_storage_host_name,
                                         CHECK_EMPTY | CHECK_VALID,
                                         ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Target Hostname'))

    if is_param(obj.input, 'network_storage_port_number'):
        check = checker.check_number(_('Target Port Number'),
                                     obj.input.network_storage_port_number,
                                     CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     PORT_MIN_NUMBER,
                                     PORT_MAX_NUMBER,
                                     ) and check

    if is_param(obj.input, 'network_storage_authentication'):
        check = checker.check_empty(_('iSCSI Authentication Type'),
                                     obj.input.network_storage_authentication,
                                     ) and check

        if obj.input.network_storage_authentication == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP:
            if is_param(obj.input, 'network_storage_user'):
                check = checker.check_username_with_num(_('iSCSI Authentication User'),
                                                        obj.input.network_storage_user,
                                                        CHECK_VALID | CHECK_LENGTH,
                                                        CHAP_USER_MIN_LENGTH,
                                                        CHAP_USER_MAX_LENGTH,
                                                        ) and check
            else:
                check = False
                checker.add_error(_('"%s" is required.') %_('iSCSI Authentication User'))


            if is_param(obj.input, 'network_storage_password'):
                check = checker.check_password(_('iSCSI Authentication Password'),
                                               obj.input.network_storage_password,
                                               obj.input.network_storage_password,
                                               CHECK_LENGTH,
                                               CHAP_PASSWORD_MIN_LENGTH,
                                               CHAP_PASSWORD_MAX_LENGTH,
                                               ) and check
            else:
                check = False
                checker.add_error(_('"%s" is required.') %_('iSCSI Authentication Password'))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('iSCSI Authentication Type'))

    obj.view.alert = checker.errors
    return check

class HostBy1NetworkStorageBy1(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if self.is_mode_input() is True:
            self.view.host_id = host_id

        iqn = self.input.iqn
        options = {'iqn' : iqn}

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_GET), options)

        cmd_name = u'Get iSCSI Detail'
        jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])
        jobgroup.jobs.append(Job('%s command' % cmd_name, 0, _cmd))
        jobgroup.type = JOBGROUP_TYPE['PARALLEL']

        host = findbyhost1(self.orm, host_id)
        _machine2jobgroup = m2j_new(machine=host,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )

        if corp(self.orm, self.pysilhouette.orm,_machine2jobgroup, jobgroup) is False:
            self.logger.debug("%s command failed. Return to timeout" % (cmd_name))
            return web.internalerror('Internal Server Error. (Timeout)')

        cmd_res = jobgroup.jobs[0].action_stdout

        if not cmd_res:
            self.view.info = {
                'type'      : "iSCSI",
                'hostname'  : "",
                'port'      : "",
                'tpgt'      : "",
                'iqn'       : "",
                'activity'  : "",
                'autostart' : "",
                'auth'      : "",
                'user'      : "",
                'disk_list' : [],
                }

            return True

        (host,port,tpgt,iqn,activity,autostart,auth,user) = cmd_res.strip("\n").split(' ', 8)
        info = {
            'type'      : "iSCSI",
            'hostname'  : host,
            'port'      : port,
            'tpgt'      : tpgt,
            'iqn'       : iqn,
            'activity'  : string.atoi(activity),
            'autostart' : string.atoi(autostart),
            'auth'      : auth,
            'user'      : user,
            'disk_list' : [],
            }

        dev_symlink_list = get_filelist(ISCSI_DEVICE_DIR)
        if activity == '1':
            disk_list = []
            symlink_regexp = re.compile("^%s" % (re.escape(ISCSI_DEVICE_NAME_TPL % (host, port, iqn))))
            for sym_link in dev_symlink_list:
                if symlink_regexp.match(sym_link):
                    real_path = symlink2real("%s/%s" % (ISCSI_DEVICE_DIR, sym_link))
                    disk_list.append({'symlink_name' : sym_link,
                                      'realpath_list' : real_path,
                                      })
            info['disk_list'] = disk_list

        self.view.info = info
        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_network_storage(self):
            self.logger.debug("Network storage update failed. Did not validate.")
            return web.badrequest(self.view.alert)

        hostname = self.input.network_storage_host_name
        port = self.input.network_storage_port_number
        iqn = self.input.network_storage_iqn
        auth = self.input.network_storage_authentication
        user = self.input.network_storage_user
        password = self.input.network_storage_password
        auto_start = False
        if is_param(self.input, 'network_storage_auto_start'):
            auto_start = True

        options = {'auth' : auth,
                   'iqn' : iqn,
                   'target' : hostname}
        if port:
            options['port'] = port

        if auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP:
            options['user'] =  user
            try:
                password_file_name = '/tmp/' + generate_phrase(12,'abcdefghijklmnopqrstuvwxyz')
                create_file(password_file_name, password)
                options['password-file'] = password_file_name
            except Exception, e:
                self.logger.error('Failed to create tmp password file. - file=%s' % (password_file_name))
                options['password'] = password

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_UPDATE), options)

        if auto_start:
            _cmd = _cmd + " --autostart"

        cmd_name = u'Update iSCSI'
        jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])
        jobgroup.jobs.append(Job('%s command' % cmd_name, 0, _cmd))

        host = findbyhost1(self.orm, host_id)
        _machine2jobgroup = m2j_new(machine=host,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )

        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               jobgroup,
                               )

        return web.accepted()

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        host = findbyhost1(self.orm, host_id)

        if is_param(self.input, "iqn"):
            iqn = self.input.iqn
        else:
            self.logger.debug("Network storage delete failed. Target IQN not found.")
            return web.badrequest()

        options = {'iqn' : iqn}
        job_order = 0
        cmd_name = u'Delete iSCSI'
        jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])

        if is_param(self.input, "host") and is_param(self.input, "port"):
            host = self.input.host
            port = self.input.port
            used_pool = []
            active_used_pool = []

            kvc = KaresansuiVirtConnection()
            try:
                dev_symlink_list = get_filelist(ISCSI_DEVICE_DIR)
                dev_symlink_list.sort()
                symlink_regexp = re.compile("^%s/%s" % (re.escape(ISCSI_DEVICE_DIR), re.escape(ISCSI_DEVICE_NAME_TPL % (host, port, iqn))))

                pools = kvc.list_active_storage_pool() + kvc.list_inactive_storage_pool()
                for pool in pools:
                    pool_type = kvc.get_storage_pool_type(pool)
                    if pool_type == "iscsi":
                        if iqn == kvc.get_storage_pool_sourcedevicepath(pool):
                            used_pool.append(pool)
                            pool_objs = kvc.search_kvn_storage_pools(pool)
                            if pool_objs[0].is_active():
                                active_used_pool.append(pool)

                    elif pool_type == "fs":
                        if symlink_regexp.match(kvc.get_storage_pool_sourcedevicepath(pool)):
                            used_pool.append(pool)
                            pool_objs = kvc.search_kvn_storage_pools(pool)
                            if pool_objs[0].is_active():
                                active_used_pool.append(pool)

            finally:
                kvc.close()

            for pool in active_used_pool:
                stop_pool_cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DESTROY_STORAGE_POOL),
                    {"name" : pool})
                stop_pool_cmdname = "Stop Storage Pool"
                jobgroup.jobs.append(Job('%s command' % stop_pool_cmdname, 0, stop_pool_cmd))
                job_order = 1

            for pool in used_pool:
                delete_pool_cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_POOL),
                    {"name" : pool})
                delete_pool_cmdname = "Delete Storage Pool"
                jobgroup.jobs.append(Job('%s command' % delete_pool_cmdname, job_order, delete_pool_cmd))
                job_order = 2

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_DELETE), options)

        jobgroup.jobs.append(Job('%s command' % cmd_name, job_order, _cmd))

        host = findbyhost1(self.orm, host_id)
        _machine2jobgroup = m2j_new(machine=host,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )

        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               jobgroup,
                               )

        return web.accepted()

urls = (
    '/host/(\d+)/networkstorage/([^\./]+)[/]?(\.part)?$', HostBy1NetworkStorageBy1,
    )
