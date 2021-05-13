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
from karesansui.lib.const import VIRT_COMMAND_DELETE_STORAGE_POOL

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID


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

def delete_storage_pool_job(obj, host, name, options={}):
    #:TODO
    options['name'] = name

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_POOL), options)

    cmdname = "Delete Storage Pool"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job("%s command" % cmdname, 0, _cmd))

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
    return True

class HostBy1StoragePoolBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        uuid = param[1]

        if not validates_storage_pool(self, uuid):
            self.logger.debug("Get storage pool info failed. Did not validate.")
            return web.badrequest(self.view.alert)

        try:
            kvc = KaresansuiVirtConnection()
            inactive_pool = kvc.list_inactive_storage_pool()
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            self.view.pools = pools
            pools_obj = kvc.get_storage_pool_UUIDString2kvn_storage_pool(uuid)
            if len(pools_obj) <= 0:
                self.logger.debug("Get storage pool info failed. Target storage pool not found.")
                return web.notfound()

            pool_obj = pools_obj[0]
            pool_info = pool_obj.get_info()
            vols_info = []
            if pool_obj.is_active() is True:
                vols_obj = pool_obj.search_kvn_storage_volumes(kvc)
                for vol_obj in vols_obj:
                    vols_info.append(vol_obj.get_info())

        finally:
            kvc.close()

        self.view.pool_info = pool_info
        self.view.vols_info = vols_info

        return True

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        uuid = param[1]

        if not validates_storage_pool(self, uuid):
            self.logger.debug("Delete storage pool failed. Did not validate.")
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
                return web.notfound()

            if kvc.is_used_storage_pool(pools_obj[0].get_storage_name()) is True:
                self.logger.debug("Delete storage pool failed. Target storage pool is used by guest.")
                return web.badrequest("Target storage pool is used by guest.")
        finally:
            kvc.close()

        model = findbyhost1(self.orm, host_id)

        if delete_storage_pool_job(self,model,pools_obj[0].get_storage_name()) is True:
            self.logger.debug("Delete storage pool success. name=%s" % (pools_obj[0].get_storage_name()))
            return web.accepted()
        else:
            self.logger.debug("Failed delete storage pool. name=%s" % (pools_obj[0].get_storage_name()))
            return False

urls = (
    '/host/(\d+)/storagepool/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})/?(\.part)$', HostBy1StoragePoolBy1,
    )
