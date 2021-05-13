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

import os

import web

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.const import VIRT_COMMAND_DELETE_DISK, \
     DISK_USES, VIRT_COMMAND_DELETE_STORAGE_VOLUME
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.merge import MergeGuest
from karesansui.lib.utils import is_int

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

# lib public
def delete_storage_volume(obj, volume, pool, order, use=DISK_USES["DISK"]):
    cmdname = "Delete Storage Volume"
    cmd = VIRT_COMMAND_DELETE_STORAGE_VOLUME

    options = {}

    options['name'] = volume
    options['pool'] = pool
    options['use'] = use

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    job = Job('%s command' % cmdname, order, _cmd)
    return job

def delete_disk_job(obj, name, target, order, options={}):
    options['name'] = name
    options['target'] = target

    cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_DISK), options)

    job = Job('Delete disk', order, cmd)
    return job

def setexec_delete_disk(obj, guest, disk_job, volume_job):
    jobgroup = JobGroup('Delete disk', karesansui.sheconf['env.uniqkey'])
    order = 0
    if volume_job is not None:
        jobgroup.jobs.append(volume_job)
    jobgroup.jobs.append(disk_job)

    _machine2jobgroup = m2j_new(machine=guest,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           jobgroup,
                           )
    return True



class GuestBy1DiskBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.badrequest()

        disk_id = int(param[2])

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()

        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()

            virt = kvc.search_kvg_guests(domname)[0]

            guest = MergeGuest(model, virt)
            self.view.guest = guest
            self.view.disk_info = virt.get_disk_info()[disk_id]
        finally:
            kvc.close()

        return True

    """
    @auth
    def _PUT(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.badrequest()

        disk_id = int(param[2])

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            guest = MergeGuest(model, virt)
        finally:
            kvc.close()

        return web.accepted()
    """

    @auth
    def _DELETE(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.badrequest()

        disk_id = int(param[2])

        model = findbyguest1(self.orm, guest_id)
        if not model: return web.notfound()

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)

            virt = kvc.search_kvg_guests(domname)[0]
            guest = MergeGuest(model, virt)
            disk_info = virt.get_disk_info()[disk_id]

            if 'file' in disk_info['source']:
                pool_type = 'file'
                volume_rpath = disk_info['source']['file']
            elif 'dev' in disk_info['source']:
                pool_type = 'iscsi'
                volume_rpath = disk_info['source']['dev']

            disk_type = disk_info['type']
            disk_device = disk_info['device']

            if disk_device != "cdrom":
                pool_name = kvc.get_storage_pool_name_byimage(volume_rpath)
                if not pool_name:
                    return web.badrequest(_("Storage pool not found."))
                else:
                    pool_name = pool_name[0]
                pool_type = kvc.get_storage_pool_type(pool_name)

            order = 0
            volume_job = None
            if pool_type != 'iscsi' and disk_type != "block":
                disk_volumes = kvc.get_storage_volume_bydomain(domname, 'disk', 'key')
                volume = None

                for key in list(disk_volumes.keys()):
                    if volume_rpath == os.path.realpath(disk_volumes[key]):
                        volume = key

                if volume is None:
                    return web.badrequest(_("Storage volume can not be found."))

                volume_job = delete_storage_volume(self,
                                                   key,
                                                   pool_name,
                                                   order,
                                                   use=DISK_USES["DISK"]
                                                   )
                order += 1
        finally:
            kvc.close()

        target = disk_info["target"]["dev"]
        self.logger.debug('spinning off delete_disk_job dom=%s, target=%s' % (domname, target))

        disk_job = delete_disk_job(self, domname, target, order)
        if setexec_delete_disk(self, model, disk_job, volume_job) is True:
            return web.accepted()
        else:
            return False

urls = (
    '/host/(\d+)/guest/(\d+)/disk/(\d+)/?(\.part|\.json)?$', GuestBy1DiskBy1,
    )
