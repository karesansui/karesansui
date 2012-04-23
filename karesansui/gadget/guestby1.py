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
from web.utils import Storage

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import \
    comma_split, uniq_sort, is_param, json_dumps

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_LENGTH, CHECK_ONLYSPACE

from karesansui.lib.const import \
    NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH, \
    MACHINE_NAME_MIN_LENGTH, MACHINE_NAME_MAX_LENGTH, \
    TAG_MIN_LENGTH, TAG_MAX_LENGTH, \
    VIRT_COMMAND_DELETE_GUEST, VIRT_COMMAND_DELETE_STORAGE_VOLUME, \
    DISK_USES

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.merge import MergeGuest

from karesansui.db.access.machine import \
     findbyguest1, findby1name, logical_delete, \
     update as m_update, delete as m_delete

from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.tag import \
     new as t_new, samecount as t_count, findby1name as t_name

from karesansui.db.model._2pysilhouette import Job, JobGroup

from karesansui.gadget.guestby1diskby1 import delete_storage_volume, delete_disk_job
from pysilhouette.command import dict2command

def validates_guest_edit(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'm_name'):
        check = False
        checker.add_error(_('Parameter m_name does not exist.'))
    else:
        check = checker.check_string(
                    _('Machine Name'),
                    obj.input.m_name,
                    CHECK_EMPTY | CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = MACHINE_NAME_MIN_LENGTH,
                    max = MACHINE_NAME_MAX_LENGTH,
            ) and check

    if is_param(obj.input, 'note_title'):
        check = checker.check_string(
                    _('Title'),
                    obj.input.note_title,
                    CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = NOTE_TITLE_MIN_LENGTH,
                    max = NOTE_TITLE_MAX_LENGTH,
                ) and check

    if is_param(obj.input, 'note_value'):
        check = checker.check_string(
                    _('Note'),
                    obj.input.note_value,
                    CHECK_ONLYSPACE,
                    None,
                    None,
                    None,
                ) and check


    if is_param(obj.input, 'tags'):
        for tag in comma_split(obj.input.tags):
            check = checker.check_string(
                        _('Tag'),
                        tag,
                        CHECK_LENGTH | CHECK_ONLYSPACE,
                        None,
                        min = TAG_MIN_LENGTH,
                        max = TAG_MAX_LENGTH,
                    ) and check

    obj.view.alert = checker.errors
    return check

class GuestBy1(Rest):

    def _post(self, f):
        ret = Rest._post(self, f)
        if hasattr(self, "kvc") is True:
            self.kvc.close()
        return ret

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)

        if self.input.has_key('job_id') is True:
            self.view.job_id = self.input.job_id
        else:
            self.view.job_id = None

        if guest_id is None:
            return web.notfound()

        model = findbyguest1(self.orm, guest_id)

        self.kvc = KaresansuiVirtConnection()
        if self.is_mode_input() is True:
            try:
                domname = self.kvc.uuid_to_domname(model.uniq_key)
                if not domname:
                    return web.notfound()

                virt = self.kvc.search_kvg_guests(domname)[0]
                guest = MergeGuest(model, virt)
                self.view.model = guest.info["model"]
                return True
            except:
                self.kvc.close()
                raise
        else:
            try:
                domname = self.kvc.uuid_to_domname(model.uniq_key)
                if not domname:
                    return web.notfound()

                virt = self.kvc.search_kvg_guests(domname)[0]

                guest = MergeGuest(model, virt)

                guest_info = guest.info["virt"].get_info()
                info = {}
                info['memory'] = guest_info["memory"]
                info['cpu'] = guest_info["cpuTime"]
                info['os'] = guest_info["OSType"]
                info['hypervisor'] = guest_info["hypervisor"]
                info['type'] = guest_info["VMType"]
                info['hv_version'] = guest_info["hv_version"]

                disk_info = guest.info["virt"].get_disk_info()
                interface_info = guest.info["virt"].get_interface_info()
                net_info = guest.info["virt"].get_netinfo()
                graphics_info = guest.info["virt"].get_graphics_info()
                vcpu_info = guest.info["virt"].get_vcpus_info()

                pool_info = []
                pool_vols_info = []
                already_vols = []
                pools = self.kvc.get_storage_pool_name_bydomain(domname)
                if len(pools) > 0:
                    for pool in pools:
                        pool_obj = self.kvc.search_kvn_storage_pools(pool)[0]
                        if pool_obj.is_active() is True:
                            pool_info = pool_obj.get_info()

                            vols_obj = pool_obj.search_kvn_storage_volumes(self.kvc)
                            vols_info = {}

                            for vol_obj in vols_obj:
                                vol_name = vol_obj.get_storage_volume_name()
                                vols_info[vol_name] = vol_obj.get_info()

                            pool_vols_info = vols_info

                if self.__template__["media"] == 'json':
                    json_guest = guest.get_json(self.me.languages)
                    self.view.data = json_dumps(
                        {
                            "model": json_guest["model"],
                            "virt": json_guest["virt"],
                            "autostart": guest.info["virt"].autostart(),
                            "info": info,
                            "disk_info": disk_info,
                            "net_info": net_info,
                            "interface_info": interface_info,
                            "pool_info": pool_info,
                            "pool_vols_info": pool_vols_info,
                            "graphics_info": graphics_info,
                            "vcpu_info": vcpu_info,
                        }
                    )
                else:
                    self.view.model = guest.info["model"]
                    self.view.virt = guest.info["virt"]
                    self.view.autostart = guest.info["virt"].autostart()
                    self.view.info = info
                    self.view.disk_info = disk_info
                    self.view.net_info = net_info
                    self.view.interface_info = interface_info
                    self.view.pool_info = pool_info
                    self.view.pool_vols_info = pool_vols_info
                    self.view.graphics_info = graphics_info
                    self.view.vcpu_info = vcpu_info
            except:
                self.kvc.close()
                raise

            return True

    @auth
    def _PUT(self, *param, **params):

        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None:
            return web.notfound()

        if not validates_guest_edit(self):
            self.logger.debug("Update Guest OS is failed, Invalid input value.")
            return web.badrequest(self.view.alert)

        guest = findbyguest1(self.orm, guest_id)

        # notebook
        if is_param(self.input, "note_title"):
            guest.notebook.title = self.input.note_title
        if is_param(self.input, "note_value"):
            guest.notebook.value = self.input.note_value

        if is_param(self.input, "m_name"):
            guest.name = self.input.m_name

        # Icon
        icon_filename = None
        if is_param(self.input, "icon_filename", empty=True):
            guest.icon = self.input.icon_filename

        # tag UPDATE
        if is_param(self.input, "tags"):
            _tags = []
            tag_array = comma_split(self.input.tags)
            tag_array = uniq_sort(tag_array)
            for x in tag_array:
                if t_count(self.orm, x) == 0:
                    _tags.append(t_new(x))
                else:
                    _tags.append(t_name(self.orm, x))
            guest.tags = _tags

        guest.modified_user = self.me

        m_update(self.orm, guest)
        return web.seeother(web.ctx.path)


    @auth
    def _DELETE(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None:
            return web.notfound()

        model = findbyguest1(self.orm, guest_id)

        self.kvc = KaresansuiVirtConnection()
        try:
            domname = self.kvc.uuid_to_domname(model.uniq_key)
            if not domname:
                self.logger.info("Did not exist in libvirt. - guestid=%s" % model.id)
                logical_delete(self.orm, model)
                # TODO ファイルシステムにゴミが残るので、delete_guest.pyを実行する必要がある。
                self.orm.commit()
                return web.nocontent()

            kvg_guest = self.kvc.search_kvg_guests(domname)
            if not kvg_guest:
                return web.badrequest(_("Guest not found. - name=%s") % domname)
            else:
                kvg_guest = kvg_guest[0]

            if kvg_guest.is_active():
                return web.badrequest(_("Can not delete a running guest OS. - name=%s") % domname)

            # jobs order
            order = 0

            jobs = []
            os_storage = {}
            for disk in kvg_guest.get_disk_info():
                if disk['type'] == 'file': # type="dir"
                    # delete_storage_volume
                    pool = self.kvc.get_storage_pool_name_byimage(disk['source']['file'])
                    if not pool:
                        return web.badrequest(_("Can not find the storage pool image. - target=%s") % (disk['source']['file']))
                    else:
                        pool = pool[0]

                    disk_volumes = self.kvc.get_storage_volume_bydomain(domname, 'disk', 'key')
                    volume = None
                    for key in disk_volumes.keys():
                        if disk['source']['file'] == os.path.realpath(disk_volumes[key]):
                            volume = key # disk image

                    use = DISK_USES['DISK']
                    if volume is None: # os image
                        os_volume = self.kvc.get_storage_volume_bydomain(domname, 'os', 'key')
                        if not os_volume:
                            return web.badrequest(_("OS storage volume for guest could not be found. domname=%s") % domname)

                        if disk['source']['file'] == os.path.realpath(os_volume.values()[0]):
                            use = DISK_USES['IMAGES']
                            volume = os_volume.keys()[0]
                            os_storage["pool"] = pool
                            os_storage["volume"] = volume
                            continue # OS delete command to do "VIRT_COMMAND_DELETE_GUEST" image.

                    jobs.append(delete_storage_volume(self,
                                                      volume,
                                                      pool,
                                                      order,
                                                      use))
                    order += 1

                    # delete_disk
                    jobs.append(delete_disk_job(self,
                                               domname,
                                               disk["target"]["dev"],
                                               order))
                    order += 1

                elif disk['type'] == 'block': # type="iscsi"

                    pool = self.kvc.get_storage_pool_name_byimage(disk['source']['dev'])
                    if not pool:
                        return web.badrequest(_("Can not find the storage pool image. - target=%s") % disk['source']['dev'])
                    else:
                        pool = pool[0]

                    os_volume = self.kvc.get_storage_volume_bydomain(domname, 'os', 'key')
                    if not os_volume:
                        return web.badrequest(_("OS storage volume for guest could not be found. domname=%s") % domname)
                    else:
                        volume = os_volume.values()[0]
                        if disk['source']['dev'] == volume:
                            os_storage["pool"] = pool
                            os_storage["volume"] = volume
                            continue # OS delete command to do "VIRT_COMMAND_DELETE_GUEST" image.

                    # delete_disk
                    jobs.append(delete_disk_job(self,
                                               domname,
                                               disk["target"]["dev"],
                                               order))
                    order += 1
                else:
                    return web.internalerror(
                        _("Not expected storage type. type=%") % disk['type'])


            # DELETE GUEST
            cmdname = "Delete Guest"
            _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
            _jobgroup.jobs = jobs # Set Disk
            action_cmd = dict2command(
                "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_GUEST),
                {"name" : domname,
                 "pool" : os_storage["pool"],
                 "volume" : os_storage["volume"],
                 }
                )

            _job = Job('%s command' % cmdname, order, action_cmd)
            _jobgroup.jobs.append(_job)

            logical_delete(self.orm, model)

            _machine2jobgroup = m2j_new(machine=model,
                                        jobgroup_id=-1,
                                        uniq_key=karesansui.sheconf['env.uniqkey'],
                                        created_user=self.me,
                                        modified_user=self.me,
                                        )

            save_job_collaboration(self.orm,
                                   self.pysilhouette.orm,
                                   _machine2jobgroup,
                                   _jobgroup,
                                   )

            return web.accepted(url = web.ctx.path)
        finally:
            #self.kvc.close() GuestBy1#_post
            pass

urls = (
    '/host/(\d+)/guest/(\d+)/?(\.html|\.part|\.json)?$', GuestBy1,
    )
