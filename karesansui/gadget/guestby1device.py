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

import re
import os
import pwd

import web

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.merge import MergeGuest
from karesansui.lib.utils import get_ifconfig_info, generate_mac_address, is_param, \
     generate_uuid, string_from_uuid

from karesansui.gadget.guestby1disk import create_disk_job, validates_disk, \
     create_storage_volume_dir, exec_disk_job

from karesansui.gadget.guestby1nic import create_nic_job, validates_nic

from karesansui.gadget.hostby1networkstorage import get_iscsi_cmd

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

from karesansui.lib.const import DISK_QEMU_FORMAT, DISK_NON_QEMU_FORMAT, \
     STORAGE_VOLUME_PWD, DISK_USES, \
     VIRT_COMMAND_DELETE_STORAGE_VOLUME, VIRT_COMMAND_CREATE_STORAGE_VOLUME

from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
     CHECK_STARTROOT, CHECK_EXIST, CHECK_ISDIR

class GuestBy1Device(Rest):

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        bridge_prefix = {
                          "XEN":"xenbr",
                          "KVM":"br|bondbr",
                          #"KVM":"eth|bondbr",
                        }

        model = findbyguest1(self.orm, guest_id)

        # virt
        self.kvc = KaresansuiVirtConnection()
        try:
            domname = self.kvc.uuid_to_domname(model.uniq_key)
            if not domname:
                return web.notfound()
            virt = self.kvc.search_kvg_guests(domname)[0]
            guest = MergeGuest(model, virt)
            self.view.guest = guest

            # Output .input
            if self.is_mode_input() is True:
                try:
                    VMType = guest.info["virt"].get_info()["VMType"].upper()
                except:
                    VMType = "KVM"

                self.view.VMType = VMType

                # Network
                phydev = []
                phydev_regex = re.compile(r"%s" % bridge_prefix[VMType])

                for dev,dev_info in get_ifconfig_info().iteritems():
                    try:
                        if phydev_regex.match(dev):
                            phydev.append(dev)
                    except:
                        pass
                if len(phydev) == 0:
                    phydev.append("%s0" % bridge_prefix[VMType])

                phydev.sort()
                self.view.phydev = phydev # Physical device
                self.view.virnet = sorted(self.kvc.list_active_network()) # Virtual device
                self.view.mac_address = generate_mac_address() # new mac address

                # Disk
                inactive_pool = []
                active_pool = self.kvc.list_active_storage_pool()
                pools = inactive_pool + active_pool
                pools.sort()

                if not pools:
                    return web.badrequest('One can not start a storage pool.')

                pools_info = {}
                pools_vols_info = {}
                pools_iscsi_blocks = {}
                already_vols = []
                guests = []

                guests += self.kvc.list_inactive_guest()
                guests += self.kvc.list_active_guest()
                for guest in guests:
                    already_vol = self.kvc.get_storage_volume_bydomain(domain=guest,
                                                                       image_type=None,
                                                                       attr='path')
                    if already_vol:
                        already_vols += already_vol.keys()

                for pool in pools:
                    pool_obj = self.kvc.search_kvn_storage_pools(pool)[0]
                    if pool_obj.is_active() is True:
                        pools_info[pool] = pool_obj.get_info()

                        blocks = None
                        if pools_info[pool]['type'] == 'iscsi':
                            blocks = self.kvc.get_storage_volume_iscsi_block_bypool(pool)
                            if blocks:
                                pools_iscsi_blocks[pool] = []
                        vols_obj = pool_obj.search_kvn_storage_volumes(self.kvc)
                        vols_info = {}

                        for vol_obj in vols_obj:
                            vol_name = vol_obj.get_storage_volume_name()
                            vols_info[vol_name] = vol_obj.get_info()
                            if blocks:
                                if vol_name in blocks and vol_name not in already_vols:
                                    pools_iscsi_blocks[pool].append(vol_obj.get_info())

                        pools_vols_info[pool] = vols_info

                self.view.pools = pools
                self.view.pools_info = pools_info
                self.view.pools_vols_info = pools_vols_info
                self.view.pools_iscsi_blocks = pools_iscsi_blocks

                if VMType == "KVM":
                    self.view.DISK_FORMATS = DISK_QEMU_FORMAT
                else:
                    self.view.DISK_FORMATS = DISK_NON_QEMU_FORMAT

                self.view.bus_types = self.kvc.bus_types

            else: # .part
                self.view.ifinfo = virt.get_interface_info() # interface info
                self.view.disk_info = virt.get_disk_info() # Disk info

        finally:
            self.kvc.close()

        return True

    @auth
    def _POST(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            nic_info = virt.get_interface_info()

            # -- Nic
            if self.input.device_type == "nic":
                if not validates_nic(self):
                    return web.badrequest(self.view.alert)

                f_chk = True
                for x in nic_info:
                    if x['mac']['address'] == self.input.mac_address:
                        f_chk = False
                        break
                if f_chk is False:
                    return web.badrequest(_('Specified MAC address is already defined.'))

                mac = self.input.mac_address
                bridge = None
                network = None
                if self.input.nic_type == "phydev":
                    bridge = self.input.phydev
                elif self.input.nic_type == "virnet":
                    network = self.input.virnet

                self.logger.debug('spinning off create_nic_job dom=%s, mac=%s, bridge=%s, network=%s' \
                                  % (domname, mac, bridge, network))

                create_nic_job(self,model,domname,mac,bridge,network)
                return web.accepted()

            # -- Disk
            elif self.input.device_type == "disk":
                if not validates_disk(self):
                    return web.badrequest(self.view.alert)

                volume_job = None
                order = 0
                if self.input.pool_type == "dir" or self.input.pool_type == "fs": # create(dir)
                    disk_type = 'file'
                    pool_name = self.input.pool_dir
                    volume_name = string_from_uuid(generate_uuid())
                    volume_job = create_storage_volume_dir(self,
                                                           model,
                                                           domname,
                                                           volume_name,
                                                           self.input.pool_dir,
                                                           self.input.disk_format,
                                                           self.input.disk_size,
                                                           self.input.disk_size,
                                                           'M',
                                                           order)
                    order += 1

                elif self.input.pool_type == "block": # create(iscsi block)
                    disk_type = 'iscsi'
                    (iscsi_pool, iscsi_volume) = self.input.pool_dir.split("/", 2)
                    pool_name = iscsi_pool
                    volume_name = iscsi_volume

                else:
                    return badrequest(_("No storage type specified."))

                # add disk
                disk_job = create_disk_job(self,
                                           guest=model,
                                           domain_name=domname,
                                           pool=pool_name,
                                           volume=volume_name,
                                           bus=self.input.bus_type,
                                           format=self.input.disk_format,
                                           type=disk_type,
                                           order=order)
                order += 1

                if exec_disk_job(obj=self,
                                 guest=model,
                                 disk_job=disk_job,
                                 volume_job=volume_job,
                                 order=order
                                 ) is True:
                    return web.accepted()
                else:
                    return False

            else: # Not Found
                return False
        finally:
            kvc.close()

urls = (
    '/host/(\d+)/guest/(\d+)/device/?(\.part|\.html)?$', GuestBy1Device,
    )
