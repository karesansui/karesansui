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
from web.utils import Storage

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.const import VIRT_COMMAND_START_STORAGE_POOL, \
    VIRT_COMMAND_DESTROY_STORAGE_POOL, ISCSI_COMMAND_START

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID

# storage pool status
STORAGE_POOL_START = 0;
STORAGE_POOL_STOP = 1;

def validates_storage_pool(obj, uuid=None):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if uuid:
        check = checker.check_unique_key(_('Target UUID'),
                                         uuid,
                                         CHECK_EMPTY | CHECK_VALID,
                                         ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Target UUID'))

    obj.view.alert = checker.errors
    return check

class HostBy1StoragePoolBy1Status(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        uuid = param[1]

        if not validates_storage_pool(self, uuid):
            self.logger.debug("Get storage pool status failed. Did not validate.")
            return web.badrequest(self.view.alert)

        # Pool
        try:
            kvc = KaresansuiVirtConnection()
            inactive_pool = kvc.list_inactive_storage_pool()
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            self.view.pools = pools

            pools_obj = kvc.get_storage_pool_UUIDString2kvn_storage_pool(uuid)
            if len(pools_obj) <= 0:
                self.logger.debug("Get storage pool status failed. Target storage pool not found.")
                return web.notfound()

            status = STORAGE_POOL_STOP
            if pools_obj[0].is_active() is True:
                status = STORAGE_POOL_START

            if self.__template__["media"] == 'json':
                self.view.status = json_dumps(status)
            else:
                self.view.status = status

            return True
        finally:
            kvc.close()

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        uuid = param[1]

        if not validates_storage_pool(self, uuid):
            self.logger.debug("Set storage pool status failed. Did not validate.")
            return web.badrequest(self.view.alert)

        model = findbyhost1(self.orm, host_id)

        # Pool
        try:
            kvc = KaresansuiVirtConnection()
            inactive_pool = kvc.list_inactive_storage_pool()
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            self.view.pools = pools

            pools_obj = kvc.get_storage_pool_UUIDString2kvn_storage_pool(uuid)
            if len(pools_obj) <= 0:
                self.logger.debug("Set storage pool status failed. Target storage pool not found.")
                return web.notfound()

            status = int(self.input.status)
            if status == STORAGE_POOL_START:
                storagepool_start_stop_job(self, model, pools_obj[0], 'start')
            elif status == STORAGE_POOL_STOP:
                if kvc.is_used_storage_pool(name=pools_obj[0].get_storage_name(),
                                            active_only=True) is True:
                    self.logger.debug("Stop storage pool failed. Target storage pool is used by guest.")
                    return web.badrequest("Target storage pool is used by guest.")
                else:
                    storagepool_start_stop_job(self, model, pools_obj[0], 'stop')
            else:
                self.logger.debug("Set storage pool status failed. Unknown status type.")
                return web.badrequest()

            return web.accepted()
        finally:
            kvc.close()

def storagepool_start_stop_job(obj, host, pool_obj, status):
    _iscsi_job = None

    if status == 'start':
        pool_info = pool_obj.get_info()
        if pool_info['type'].lower() == "iscsi":
            _cmd = dict2command(
                "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_START),
                {"iqn" : pool_info['source']['dev_path']})
            cmdname = "Start iSCSI"
            _iscsi_job = Job('%s command' % cmdname, 0, _cmd)

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_START_STORAGE_POOL),
            {"name" : pool_obj.get_storage_name()})
        cmdname = "Start Storage Pool"
    else:
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DESTROY_STORAGE_POOL),
            {"name" : pool_obj.get_storage_name()})
        cmdname = "Stop Storage Pool"

    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])

    if _iscsi_job:
        _jobgroup.jobs.append(_iscsi_job)
        _job = Job('%s command' % cmdname, 1, _cmd)
    else:
        _job = Job('%s command' % cmdname, 0, _cmd)

    _jobgroup.jobs.append(_job)

    _machine2jobgroup = m2j_new(machine=host,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )

urls = (
    '/host/(\d+)/storagepool/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})/status/?(\.part)$', HostBy1StoragePoolBy1Status,
    )
