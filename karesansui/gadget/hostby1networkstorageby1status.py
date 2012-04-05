# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import web
import re

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.db.model._2pysilhouette import Job, JobGroup, JOBGROUP_TYPE
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import jg_findby1, jg_save
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from pysilhouette.command import dict2command

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.utils import is_param, get_filelist, uniq_sort
from karesansui.lib.const import ISCSI_COMMAND_START, ISCSI_COMMAND_STOP, \
    ISCSI_DEVICE_NAME_TPL, ISCSI_DEVICE_DIR, \
    VIRT_COMMAND_DESTROY_STORAGE_POOL, VIRT_COMMAND_START_STORAGE_POOL, \
    PORT_MIN_NUMBER, PORT_MAX_NUMBER

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID, \
    CHECK_MIN, CHECK_MAX, CHECK_ONLYSPACE

NETWORK_STORAGE_START = "0"
NETWORK_STORAGE_STOP = "1"

def validates_network_storage(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'iqn'):
        check = checker.check_string(_('Target IQN'),
                                     obj.input.iqn,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     None,
                                     None,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Target IQN'))

    if is_param(obj.input, 'status'):
        check = checker.check_empty(_('Action Status'),
                                     obj.input.status,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Action Status'))

    if is_param(obj.input, 'host'):
        check = checker.check_domainname(_('Target Hostname'),
                                         obj.input.host,
                                         CHECK_EMPTY | CHECK_VALID,
                                         ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Target Hostname'))

    if is_param(obj.input, 'port'):
        check = checker.check_number(_('Target Port Number'),
                                     obj.input.port,
                                     CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     PORT_MIN_NUMBER,
                                     PORT_MAX_NUMBER,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Target Port Number'))

    obj.view.alert = checker.errors
    return check

class HostBy1NetworkStorageBy1Status(Rest):
    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_network_storage(self):
            self.logger.debug("Network storage change status failed. Did not validate.")
            return web.badrequest(self.view.alert)

        host = findbyhost1(self.orm, host_id)

        if is_param(self.input, "iqn"):
            iqn = self.input.iqn
        else:
            self.logger.debug("Network storage change status failed. Target IQN not found.")
            return web.badrequest()

        options = {'iqn' : iqn}
        job_order = 0

        if is_param(self.input, "status"):
            status = self.input.status
        else:
            self.logger.debug("Network storage change status failed. Status type not found.")
            return web.badrequest()

        if is_param(self.input, "host") and is_param(self.input, "port"):
            host = self.input.host
            port = self.input.port
        else:
            self.logger.debug("Network storage change status failed. Target host and port not found.")
            return web.badrequest()

        active_used_pool = []
        inactive_used_pool = []

        kvc = KaresansuiVirtConnection()
        try:
            dev_symlink_list = get_filelist(ISCSI_DEVICE_DIR)
            dev_symlink_list.sort()
            symlink_regexp = re.compile("^%s/%s" % (re.escape(ISCSI_DEVICE_DIR), re.escape(ISCSI_DEVICE_NAME_TPL % (host, port, iqn))))

            active_pools = kvc.list_active_storage_pool()
            inactive_pools = kvc.list_inactive_storage_pool()
            now_pools = active_pools + inactive_pools
            for pool in now_pools:
                pool_type = kvc.get_storage_pool_type(pool)
                if pool_type == "iscsi":
                    if iqn == kvc.get_storage_pool_sourcedevicepath(pool):
                        if pool in active_pools:
                            active_used_pool.append(pool)
                        if pool in inactive_pools:
                            inactive_used_pool.append(pool)
                elif pool_type == "fs":
                    if symlink_regexp.match(kvc.get_storage_pool_sourcedevicepath(pool)):
                        if pool in active_pools:
                            active_used_pool.append(pool)
                        if pool in inactive_pools:
                            inactive_used_pool.append(pool)

            if status == NETWORK_STORAGE_STOP:
                for pool in active_used_pool:
                    if kvc.is_used_storage_pool(name=pool, active_only=True) is True:
                        self.logger.debug("Stop iSCSI failed. Target iSCSI is used by guest.")
                        return web.badrequest("Target iSCSI is used by guest.")
        finally:
            kvc.close()

        if status == NETWORK_STORAGE_START:
            network_storage_cmd = ISCSI_COMMAND_START
            cmd_name = u'Start iSCSI'
            jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])

            for pool in inactive_used_pool:
                pool_cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_START_STORAGE_POOL),
                    {"name" : pool})
                pool_cmdname = "Start Storage Pool"
                jobgroup.jobs.append(Job('%s command' % pool_cmdname, 1, pool_cmd))
                job_order = 0

        elif status == NETWORK_STORAGE_STOP:
            network_storage_cmd = ISCSI_COMMAND_STOP
            cmd_name = u'Stop iSCSI'
            jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])

            for pool in active_used_pool:
                pool_cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DESTROY_STORAGE_POOL),
                    {"name" : pool})
                pool_cmdname = "Stop Storage Pool"
                jobgroup.jobs.append(Job('%s command' % pool_cmdname, 0, pool_cmd))
                job_order = 1

        else:
            return web.internalerror('Internal Server Error. (Param)')

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], network_storage_cmd), options)

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
    '/host/(\d+)/networkstorage/([^\./]+)/status/?(\.part)?$', HostBy1NetworkStorageBy1Status,
    )
