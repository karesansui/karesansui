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

from karesansui.lib.utils import is_param, generate_phrase, create_file, \
    get_filelist, symlink2real
from karesansui.lib.const import ISCSI_COMMAND_GET, ISCSI_COMMAND_ADD, \
    ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    CHAP_USER_MIN_LENGTH,                CHAP_USER_MAX_LENGTH, \
    CHAP_PASSWORD_MIN_LENGTH,            CHAP_PASSWORD_MAX_LENGTH, \
    ISCSI_DEVICE_DIR,                    ISCSI_DEVICE_NAME_TPL

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_MIN, CHECK_MAX


def get_network_storages(data):
    network_storages = []
    dev_symlink_list = get_filelist(ISCSI_DEVICE_DIR)
    dev_symlink_list.sort()
    unmountable_regexp = re.compile("-part[0-9]+$")
    for line in data.split('\n'):
        if not line:
            continue

        (host,port,tpgt,iqn,activity,autostart) = line.split(' ', 6)
        node = {
            'type'      : "iSCSI",
            'hostname'  : host,
            'port'      : port,
            'tpgt'      : tpgt,
            'iqn'       : iqn,
            'activity'  : string.atoi(activity),
            'autostart' : string.atoi(autostart),
            'disk_list' : [],
            }

        if activity == '1':
            disk_list = []
            symlink_regexp = re.compile("^%s" % (re.escape(ISCSI_DEVICE_NAME_TPL % (host, port, iqn))))
            unmountable_flag = {}
            for sym_link in dev_symlink_list:
                if symlink_regexp.search(sym_link):
                    real_path = symlink2real("%s/%s" % (ISCSI_DEVICE_DIR, sym_link))
                    is_blockable = True
                    if unmountable_regexp.search(sym_link):
                        is_blockable = False
                        unmountable_flag[unmountable_regexp.sub("", sym_link)] = True

                    disk_list.append({'symlink_name'     : sym_link,
                                      'realpath_list'    : real_path,
                                      'is_blockable'     : is_blockable,
                                      'is_partitionable' : False,
                                      })

            for disk in disk_list:
                for key in unmountable_flag.keys():
                    if disk['symlink_name'] == key:
                        disk['is_partitionable'] = True

            node['disk_list'] = disk_list

        network_storages.append(node)
    return network_storages

def get_iscsi_cmd(obj, host_id):
    cmd_name = u'Get iSCSI List'
    jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])
    jobgroup.jobs.append(Job('%s command' % cmd_name, 0, "%s/%s" \
                             % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_GET)))
    jobgroup.type = JOBGROUP_TYPE['PARALLEL']

    host = findbyhost1(obj.orm, host_id)
    _machine2jobgroup = m2j_new(machine=host,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )
    if corp(obj.orm, obj.pysilhouette.orm,_machine2jobgroup, jobgroup) is False:
        return False

    ret = jobgroup.jobs[0].action_stdout
    network_storages = get_network_storages(ret)
    return network_storages

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

class HostBy1NetworkStorage(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if self.is_mode_input() is True:
            self.view.host_id = host_id
            self.view.info = {
                'type' : "iSCSI",
                'hostname' : "",
                'port' : "3260",
                'tpgt' : "",
                'iqn'  : "",
                'activity' : "",
                'autostart' : "",
                'auth' : "",
                'user' : "",
                }

            return True

        network_storages = get_iscsi_cmd(self, host_id)
        if network_storages is False:
            self.logger.debug("Get iSCSI List command failed. Return to timeout")
            #return web.internalerror('Internal Server Error. (Timeout)')

        self.view.network_storages = network_storages
        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_network_storage(self):
            self.logger.debug("Network storage add failed. Did not validate.")
            return web.badrequest(self.view.alert)

        hostname = self.input.network_storage_host_name
        port = self.input.network_storage_port_number
        auth = self.input.network_storage_authentication
        user = self.input.network_storage_user
        password = self.input.network_storage_password
        auto_start = False
        if is_param(self.input, 'network_storage_auto_start'):
            auto_start = True

        options = {'auth' : auth}
        if port:
            options['target'] = "%s:%s" % (hostname, port)
        else:
            options['target'] = hostname

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
            "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_ADD), options)

        if auto_start:
            _cmd = _cmd + " --autostart"

        cmd_name = u'Add iSCSI'
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

urls = (
    '/host/(\d+)/networkstorage[/]?(\.part)?$', HostBy1NetworkStorage,
    )

