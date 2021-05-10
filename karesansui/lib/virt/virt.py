#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

""" 
<comment-ja>
仮想化全般のライブラリ群
</comment-ja>
<comment-en>
</comment-en>

@file:   virt.py

@author: Taizo ITO <taizo@karesansui-project.info>

@copyright:    

"""

import sys
import string
import os, os.path
import time
import tempfile
import re
import libvirt
import libvirtmod
import logging
import glob

# define
from libvirt import VIR_DOMAIN_NOSTATE,VIR_DOMAIN_RUNNING,\
     VIR_DOMAIN_BLOCKED,VIR_DOMAIN_PAUSED,VIR_DOMAIN_SHUTDOWN,\
     VIR_DOMAIN_SHUTOFF,VIR_DOMAIN_CRASHED,\
     VIR_STORAGE_POOL_DELETE_NORMAL,\
     VIR_STORAGE_POOL_DELETE_ZEROED, \
     VIR_STORAGE_VOL_DELETE_NORMAL, \
     VIR_STORAGE_VOL_DELETE_ZEROED, \
     VIR_DOMAIN_XML_SECURE, \
     VIR_DOMAIN_XML_INACTIVE, \
     VIR_DOMAIN_XML_UPDATE_CPU

if __name__ == '__main__':
    for y in [os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/../../.."),"/usr/lib/python2.6","/usr/lib/python2.6/site-packages"]:
        if (y in sys.path) is False: sys.path.insert(0, y)

import karesansui
import karesansui.lib.locale

from karesansui.lib.const import VIRT_LIBVIRT_DATA_DIR, VIRT_DOMAINS_DIR, \
     VIRT_XML_CONFIG_DIR, VIRT_NETWORK_CONFIG_DIR, VIRT_SNAPSHOT_DIR, \
     VIRT_XENDOMAINS_AUTO_DIR, VIRT_AUTOSTART_CONFIG_DIR, \
     KARESANSUI_GROUP, GRAPHICS_PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
     DEFAULT_KEYMAP, VIRT_STORAGE_CONFIG_DIR, \
     DEFAULT_KVM_DISK_FORMAT, DEFAULT_XEN_DISK_FORMAT, \
     DISK_USES, GUEST_EXPORT_FILE, KVM_BUS_TYPES, XEN_BUS_TYPES, \
     VENDOR_DATA_ISCSI_DOMAINS_DIR, ISCSI_DEVICE_DIR

from karesansui.lib.const import XEN_VIRT_CONFIG_DIR, \
     XEN_VIRTUAL_DISK_PREFIX, \
     XEN_VIRT_URI_RW, XEN_VIRT_URI_RO, \
     XEN_KARESANSUI_TMP_DIR, \
     XEN_KEYMAP_DIR

from karesansui.lib.const import KVM_VIRT_CONFIG_DIR, \
     KVM_VIRTUAL_DISK_PREFIX, \
     KVM_VIRT_URI_RW, KVM_VIRT_URI_RO, \
     KVM_KARESANSUI_TMP_DIR, \
     KVM_KEYMAP_DIR

from karesansui.lib.virt.config import ConfigParam, \
     XMLConfigGenerator, sync_config_generator, KaresansuiConfigParamException

from karesansui.lib.virt.config_network import NetworkConfigParam
from karesansui.lib.virt.config_network import NetworkXMLConfigGenerator

from karesansui.lib.virt.config_storage import StorageVolumeConfigParam, \
     StorageVolumeXMLConfigGenerator, StoragePoolConfigParam, \
     StoragePoolXMLConfigGenerator

from karesansui.lib.virt.config_export import ExportConfigParam, ExportXMLGenerator

from karesansui.lib.virt.config_capabilities import CapabilitiesConfigParam

from karesansui.lib.utils import uniq_sort            as UniqSort
from karesansui.lib.utils import generate_mac_address as GenMAC
from karesansui.lib.utils import execute_command      as ExecCmd
from karesansui.lib.utils import string_from_uuid     as StrFromUUID
from karesansui.lib.utils import generate_uuid        as GenUUID
from karesansui.lib.utils import next_number          as NextNumber
from karesansui.lib.utils import create_disk_img      as MakeDiskImage
from karesansui.lib.utils import copy_file            as CopyFile
from karesansui.lib.net.http import wget              as DownloadFile
from karesansui.lib.utils import is_uuid, get_ifconfig_info, r_chgrp, r_chmod, \
  getfilesize_str, get_filesize_MB, get_disk_img_info, available_virt_uris, \
  is_iso9660_filesystem_format, is_windows_bootable_iso, is_darwin_bootable_iso, \
  file_contents_replace, uri_split, uri_join

from karesansui.lib.utils import get_inspect_stack

from karesansui.lib.file.configfile import ConfigFile


os.environ['LIBVIRT_XM_CONFIG_DIR'] = XEN_VIRT_CONFIG_DIR

class KaresansuiVirtException(karesansui.KaresansuiLibException):
    pass

class KaresansuiVirtConnection:

    def __init__(self,uri=None,readonly=True):
        self.__prep()
        self.logger.debug(get_inspect_stack())
        try:
            self.open(uri,readonly)
        except:
            raise KaresansuiVirtException(_("Cannot open '%s'") % uri)

        self.__prep2()

    def __prep(self):
        """
        <comment-ja>
        デフォルトのストレージを作成します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        if not os.path.exists(VIRT_DOMAINS_DIR):
          os.makedirs(VIRT_DOMAINS_DIR)
        if not os.path.exists(VIRT_XML_CONFIG_DIR):
          os.makedirs(VIRT_XML_CONFIG_DIR)
        self.logger = logging.getLogger('karesansui.virt')
        if os.getuid() == 0:
            r_chgrp(VIRT_LIBVIRT_DATA_DIR,KARESANSUI_GROUP)
            r_chmod(VIRT_DOMAINS_DIR,"o-rwx")

    def __prep2(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            self.logger = logging.getLogger('karesansui.virt')
            if os.getuid() == 0:
                r_chgrp(self.config_dir,KARESANSUI_GROUP)
        except:
            pass

    def open(self, uri,readonly=True):
        """
        <comment-ja>
        libvirtのコネクションをOpenします。またそれに伴う初期化も行います。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        if uri == None:
            uris = available_virt_uris()
            try:
                uri = uris["KVM"]
            except:
                try:
                    uri = uris["XEN"]
                except:
                    raise KaresansuiVirtException("Error: You must specify connect uri.")

        if uri.lower()[0:3] == "xen":
            self.disk_prefix = XEN_VIRTUAL_DISK_PREFIX
            self.config_dir  = XEN_VIRT_CONFIG_DIR
            self.bus_types   = XEN_BUS_TYPES

            if not os.access("/proc/xen", os.R_OK):
                raise KaresansuiVirtException("Error: The system is not running under Xen kernel.")

        if uri.lower()[0:4] == "qemu":
            self.disk_prefix = KVM_VIRTUAL_DISK_PREFIX
            self.config_dir  = KVM_VIRT_CONFIG_DIR
            self.bus_types   = KVM_BUS_TYPES

            if False == True:
                raise KaresansuiVirtException("Error: The system is not running under KVM hypervisor.")

        if uri != None:
            self.uri = uri

        self.logger.debug('uid=%d' % os.getuid())
        self.logger.debug('gid=%d' % os.getgid())
        
        try:
            """
            if readonly == True:
                self.logger.info('libvirt.openReadOnly - %s' % self.uri)
                self._conn = libvirt.openReadOnly(self.uri)
            else:
                self.logger.info('libvirt.open - %s' % self.uri)
                self._conn = libvirt.open(self.uri)
            """
            self.logger.debug('libvirt.open - %s' % self.uri)
            self._conn = libvirt.open(self.uri)
        except:
            self.logger.error('failed to libvirt open - %s' % self.uri)

        self.logger.debug('succeed to libvirt open - %s' % self.uri)
        self.logger.debug('hypervisor_type - %s' % self.get_hypervisor_type())

        self.guest = KaresansuiVirtGuest(self)
        self.network = KaresansuiVirtNetwork(self)
        self.storage_volume = KaresansuiVirtStorageVolume(self)
        self.storage_pool = KaresansuiVirtStoragePool(self)
        return self._conn

    def close(self, conn=None):
        """
        <comment-ja>
        libvirtなどの仮想化コネクションをCloseします。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        self.logger.debug(get_inspect_stack())
        if conn == None:
            try:
                conn = self._conn
            except NameError:
                pass
        if conn != None:
            conn.__del__()
            self.logger.debug('succeed to libvirt close - %s' % self.uri)

    def get_hypervisor_type(self):
        """<comment-ja>
        使用中のハイパーバイザーの種類を取得する。
        @param void
        @return: hypervisor type
                 Xen or QEMU is available now (depend on libvirt API)
                 e.g. Xen QEMU Test LXC phyp OpenVZ VBox UML ONE ESX
                      XenAPI Remote
        @rtype: string (see examples in previous field '@return')
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        return self._conn.getType()

    def get_capabilities(self):
        retval = {}
        param = CapabilitiesConfigParam()
        try:
            param.load_xml_config(self._conn.getCapabilities())
            retval = {
               "host" :param.host,
               "guest":param.guest,
             }
        except:
            pass
        return retval

    def get_version(self):
        """
        <comment-ja>
        libvirtのバージョン情報を取得します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        hypervisior = self.get_hypervisior_type()
        ret = libvirtmod.virGetVersion(hypervisior)
        libVersion = ret[0]
        apiVersion = ret[1]

        libVersion_major = libVersion / 1000000
        libVersion %= 1000000
        libVersion_minor = libVersion / 1000
        libVersion_rel = libVersion % 1000
        #print "Using library: libvir %d.%d.%d" %(libVersion_major, libVersion_minor, libVersion_rel)

        apiVersion_major = apiVersion / 1000000
        apiVersion %= 1000000
        apiVersion_minor = apiVersion / 1000
        apiVersion_rel = apiVersion % 1000
        #print "Using API: %s %d.%d.%d" %(hypervisior, apiVersion_major, apiVersion_minor, apiVersion_rel)

        return { "libVersion"  : "%d.%d.%d" %(libVersion_major, libVersion_minor, libVersion_rel),
                 "apiVersion"  : "%s %d.%d.%d" %(hypervisior, apiVersion_major, apiVersion_minor, apiVersion_rel)
               }

    def get_nodeinfo(self):
        info = dict()
        data = self._conn.getInfo()
        info = {
            "model"        : data[0],
            "memory"       : data[1],
            "cpus"         : data[2],
            "mhz"          : data[3],
            "nodes"        : data[4],
            "sockets"      : data[5],
            "cores"        : data[6],
            "threads"      : data[7]
        }
        return info

    def get_mem_info(self):
        """<comment-ja>
        メモリの情報を取得する。
         - guest_alloc_mem: ゲストOSに割り当てているメモリサイズ,
         - host_max_mem: ホストOSのメモリサイズ,
         - host_free_mem: ホストOSの未割り当てメモリサイズ
         - 単位はMB
        @rtype: dict
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        active_guests = self.list_active_guest()
        inactive_guests = self.list_inactive_guest()
        info = self.get_nodeinfo()
        host_max_mem = info['memory']

        guest_alloc_mem = 0
        
        for domname in active_guests + inactive_guests:
            if not domname == "Domain-0":
                virt = self.search_kvg_guests(domname)[0]
                info = virt.get_info()
                guest_alloc_mem += int(info["maxMem"])
                
        guest_alloc_mem /= 1000  # a unit 'MB'

        host_free_mem = host_max_mem - guest_alloc_mem
        if host_free_mem < 0: host_free_mem = 0

        info = {
            'guest_alloc_mem' : guest_alloc_mem,
            'host_max_mem' : host_max_mem,
            'host_free_mem' : host_free_mem,
        }
        return info

    def is_max_vcpus(self, type=None):
        """<comment-ja>
        ゲストに割り当て可能な仮想CPU数の最大値を取得できるか。

        @param type: ハイパーバイザー
        @return: the maximum number of virtual CPUs supported for a
          guest VM of a specific type.
        @rtype: bool
        </comment-ja>
        <comment-en>
        Get the maximum number of vcpu supported for guest.

        @param type: type of hypervisor
        @return: the maximum number of vcpus
        @rtype: bool
        </comment-en>
        """
        if type is None:
            type = self.get_hypervisor_type()
        try:
            max = self._conn.getMaxVcpus(type.lower())
            return True
        except libvirt.libvirtError:
            return False

    def get_max_vcpus(self, type=None):
        """<comment-ja>
        ゲストに割り当て可能な仮想CPU数の最大値を取得する

        @param type: ハイパーバイザー
        @return: the maximum number of virtual CPUs supported for a
          guest VM of a specific type.
        @rtype: integer
        </comment-ja>
        <comment-en>
        Get the maximum number of vcpu supported for guest.

        @param type: type of hypervisor
        @return: the maximum number of vcpus
        @rtype: integer
        </comment-en>
        """
        if type is None:
            type = self.get_hypervisor_type()
        try:
            max = self._conn.getMaxVcpus(type.lower())
        except libvirt.libvirtError:
            max = 32
        return max

    def get_physical_cpus(self):
        """<comment-ja>
        物理CPU数を取得する

        @return: 物理CPU数
        @rtype: integer
        </comment-ja>
        <comment-en>
        Get the number of phisical CPUs.

        @return: the number of physical CPUs
        @rtype: integer
        </comment-en>
        """
        info = self.get_nodeinfo()
        return info['nodes'] * info['sockets'] * info['cores'] * info['threads']

    """
    Domain-U
    """
    def set_domain_name(self,name=None):
        self.guest.set_domain_name(name)
    def get_domain_name(self):
        return self.guest.get_domain_name()

    def uuid_to_domname(self, uuid):
        """
        <comment-ja>
        ゲストOSのUUIDからドメイン名を取得します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        try:
            #guest = self._conn.lookupByUUIDString(uuid)
            #return guest.name()
            for guests in self.search_guests():
                if uuid == guests.UUIDString():
                    return guests.name()
        except:
            return ''

    def domname_to_uuid(self, domname):
        """
        <comment-ja>
        ドメイン名からゲストOSのUUIDを取得します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        try:
            return self.search_guests(domname)[0].UUIDString()
        except:
            return ''


    def list_inactive_guest(self,type=None):
        """
        <comment-ja>
        現在起動していないゲストOSを取得します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        if type == "uuid":
            return self._conn.listDefinedDomains()
        else:
            return self._conn.listDefinedDomains()

    def list_active_guest(self,type=None):
        """
        <comment-ja>
        現在起動しているゲストOSを取得します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        names = []
        for id in self._conn.listDomainsID():
            dom = self._conn.lookupByID(id);
            if type == "uuid":
                names.append(dom.UUIDString())
            else:
                names.append(dom.name())
        return names

    def search_guests(self, name=None):
        """
        <comment-ja>
        ドメイン名からゲストOSを検索します。
        </comment-ja>
        <comment-en>
        </comment-en>
        """
        guests = []

        if is_uuid(name):
            name = self.uuid_to_domname(name)

        try:
            guests = self.result_search_guests
        except:
            ids = self._conn.listDomainsID()
            for id in ids:
                if self._conn.lookupByID(id).name() == "Domain-0" and self.get_hypervisor_type() == 'Xen':
                    continue
                guests.append(self._conn.lookupByID(id))
            names = self.list_inactive_guest()
            for _name in names:
                guests.append(self._conn.lookupByName(_name))
            self.result_search_guests = guests

        if name == None:
            return guests

        for guest in guests:
            if guest.name() == name:
                return [guest]

        #return []
        raise KaresansuiVirtException("guest %s not found" % name)

    def search_kvg_guests(self, name=None):
        """<comment-ja>
        指定されたゲストOSオブジェクトをKaresansuiVirtGuestオブジェクトのlistにして返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        if is_uuid(name):
            name = self.uuid_to_domname(name)

        guests = []
        for guest in self.search_guests(name):
            guests.append(
                KaresansuiVirtGuest(conn=self, name=guest.name()))

        return guests

    def list_used_graphics_port(self):
        """
        <comment-ja>
        すでにシステムで利用しているグラフィックスのポート番号を取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        ports = []
        for guest in self.search_guests(None):

            param = ConfigParam(guest.name())
            xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, guest.name())
            dom = self._conn.lookupByName(guest.name())
            if not os.path.exists(xml_file):
                if dom._conn.getURI() in list(available_virt_uris().values()):
                    ConfigFile(xml_file).write(dom.XMLDesc(0))
                    if os.getuid() == 0 and os.path.exists(xml_file):
                        r_chgrp(xml_file,KARESANSUI_GROUP)
            #param.load_xml_config(xml_file)
            param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

            graphics_port = param.graphics_port
            if graphics_port and int(graphics_port) > 0:
                ports.append(int(graphics_port))

        return UniqSort(ports)

    def list_used_mac_addr(self):
        """
        <comment-ja>
        すでにシステムで利用しているMAC Addressを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        addrs = []
        for guest in self.search_guests(None):

            param = ConfigParam(guest.name())
            xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, guest.name())
            dom = self._conn.lookupByName(guest.name())
            if not os.path.exists(xml_file):
                if dom._conn.getURI() in list(available_virt_uris().values()):
                    ConfigFile(xml_file).write(dom.XMLDesc(0))
                    if os.getuid() == 0 and os.path.exists(xml_file):
                        r_chgrp(xml_file,KARESANSUI_GROUP)
            #param.load_xml_config(xml_file)
            param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

            for info in param.interfaces:
                mac_addr = info['mac']
                addrs.append(mac_addr.lower())

        return addrs

    def set_interface_format(self, format=None):
        """
        <comment-ja>
        TODO:
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """

        if format is None:
            format = "b:xenbr0"

        self.interface_format = []
        for _format in format.split(','):
            (type, name) = _format.split(':')
            if type[0] == 'n':
                try:
                    netinfo = self.search_kvn_networks(name)[0].get_info()
                    self.interface_format.append( {"type": "bridge", "name":netinfo['bridge']['name']} )
                except:
                    raise
            else:
                self.interface_format.append( {"type": "bridge", "name":name} )

    def make_domain_dir(self, dir, name):
        """
        <comment-ja>
        'dir'(Storage Pool)で構成されたゲスト用ディレクトリ構成を作成します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        # domain dir
        domain_dir = "%s/%s" % (dir, name,)
        domain_images_dir   = "%s/images"   % (domain_dir,)
        domain_boot_dir     = "%s/boot"     % (domain_dir,)
        domain_disk_dir     = "%s/disk"     % (domain_dir,)
        # < 2.0.0
        #domain_snapshot_dir = "%s/snapshot" % (domain_dir,)

        if not os.path.exists(domain_dir):
            os.makedirs(domain_dir)
        if not os.path.exists(domain_images_dir):
            os.makedirs(domain_images_dir)
        if not os.path.exists(domain_boot_dir):
            os.makedirs(domain_boot_dir)
        if not os.path.exists(domain_disk_dir):
            os.makedirs(domain_disk_dir)
        #if not os.path.exists(domain_snapshot_dir):
        #    os.makedirs(domain_snapshot_dir)
        if os.getuid() == 0:
            r_chgrp(domain_dir,KARESANSUI_GROUP)
            r_chmod(domain_dir,"o-rwx")

        return domain_dir

    def create_guest(self, name=None, type="xen", ram=256, disk=None, disksize=1024*16, 
                     mac=None, uuid=None, kernel=None, initrd=None, iso=None, graphics=None,
                     vcpus=None, extra=None, keymap=DEFAULT_KEYMAP,
                     bus=None, disk_format=None,
                     storage_pool=None, storage_volume=None):
        """
        <comment-ja>
        ゲストOSの作成を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        param = ConfigParam(name)

        # Disk
        if type == "kvm" and iso is not None:
            param.add_disk(iso, "hdc", "cdrom") # install iso image

        if bus is not None:
            bus = bus.lower()

        # Pool
        pool_objs = self.search_kvn_storage_pools(storage_pool)
        if not pool_objs:
            raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                              storage_pool)

        pool_type = pool_objs[0].get_info()['type']

        if pool_type == 'iscsi':
            domains_dir = VENDOR_DATA_ISCSI_DOMAINS_DIR
            domain_dir = self.make_domain_dir(VENDOR_DATA_ISCSI_DOMAINS_DIR, name)
        else:
            domains_dir = pool_objs[0].get_info()["target"]["path"]
            domain_dir = self.make_domain_dir(domains_dir, name)


        if pool_type == "iscsi":
            disk_type = "block"
            disk = self.get_storage_volume_path(storage_pool, storage_volume)
        else:
            disk_type = "file"
            #disk = "%s/images/%s.img" % (domain_dir, storage_volume)
            disk = "%s/images/%s.img" % (domain_dir, name)

        if disk is None:
            raise KaresansuiVirtException("%s pool=%s,volume=%s" % \
                                          (_("Storage path could not be retrieved."),
                                           storage_pool,
                                           storage_volume
                                           ))

        driver_type = None
        driver_name = None
        try:
            file_format = get_disk_img_info(disk)['file_format']
            if file_format == "qcow2":
                driver_type = "qcow2"
                if type == "kvm":
                    driver_name = "qemu"
            if type == "kvm":
                driver_type = file_format
        except:
            pass

        if bus == "virtio":
            target_dev_prefix = "vd"
        elif bus == "scsi":
            target_dev_prefix = "sd"
        else:
            target_dev_prefix = self.disk_prefix

        param.add_disk(disk,
                       target_dev_prefix + "a",
                       bus=bus,
                       disk_type=disk_type,
                       driver_name=driver_name,
                       driver_type=driver_type)

        if mac is None:
            mac = GenMAC()

        if uuid is None:
            uuid = StrFromUUID(GenUUID())

        if vcpus is None:
            vcpus = 1

        if graphics is None:
            used_ports = self.list_used_graphics_port()
            graphics = NextNumber(GRAPHICS_PORT_MIN_NUMBER,PORT_MAX_NUMBER,used_ports)

#        if os.path.exists(disk):
#            os.unlink(disk)

        param.set_domain_type(type)
        param.set_uuid(uuid)
        if type == "kvm":
            acpi_info_file = "/proc/acpi/info"
            if os.path.exists(acpi_info_file):
                param.set_features_acpi(True)
            if iso is not None:
                param.set_boot_dev("cdrom")
                if is_windows_bootable_iso(iso) is not False:
                    param.set_features_apic(True)
                elif is_darwin_bootable_iso(iso) is not False:
                    param.set_features_apic(True)
            else:
                param.set_kernel(kernel)
                param.set_initrd(initrd)
        else:
            param.set_kernel(kernel)
            param.set_initrd(initrd)

        param.set_max_vcpus(vcpus)
        param.set_memory(str(ram) + 'm')
        param.set_graphics_keymap(keymap)

        # definition for a network interface
        if type == "kvm":
            model = "virtio"
        else:
            model = None
        for _format in self.interface_format:
            if _format['name'][0:5] == 'xenbr':
                script = "vif-bridge"
            else:
                script = None

            if mac is None:
                mac = GenMAC()
                param.add_interface(mac,"bridge",_format['name'],script,model=model)
            else:
                param.add_interface(mac.lower(),"bridge",_format['name'],script,model=model)
                mac = None

        param.set_graphics_port(graphics)
        if extra != None:
            param.append_commandline(extra)
        param.set_behavior("on_shutoff","destroy")
        param.set_behavior("on_reboot","destroy")
        param.set_behavior("on_crash","destroy")

        r = re.compile(r"""(?:ftp|http)s?://""")

        domain_boot_dir = "%s/boot" % (domain_dir,)
        if kernel is not None:
            (kfd, kfn) = tempfile.mkstemp(prefix="vmlinuz.", dir=domain_boot_dir)
            m = r.match(param.get_kernel())
            if m:
              os.close(kfd)
              DownloadFile(param.get_kernel(),kfn)
            else:
              kernel = open(param.get_kernel(),"r")
              os.write(kfd, kernel.read())
              os.close(kfd)
              kernel.close()
            param.set_kernel(kfn)

        if initrd is not None:
            (ifd, ifn) = tempfile.mkstemp(prefix="initrd.img.", dir=domain_boot_dir)
            m = r.match(param.get_initrd())
            if m:
              os.close(ifd)
              DownloadFile(param.get_initrd(),ifn)
            else:
              initrd = open(param.get_initrd(),"r")
              os.write(ifd, initrd.read())
              os.close(ifd)
              initrd.close()
            param.set_initrd(ifn)

        sync_config_generator(param)

        if self._conn is None:
            self._conn = self.open(None)

        generator = XMLConfigGenerator()
        try:
            cfgxml = generator.generate(param)
        except:
            raise

        dom = self._conn.createLinux(cfgxml, 0)
        time.sleep(2)
        self._conn.defineXML(cfgxml)
        time.sleep(1)
        try:
            self._conn.lookupByID(dom.ID())
        except libvirt.libvirtError:
            raise KaresansuiVirtException("create_guest() error. name:%s" % (name))

        if initrd is not None:
            os.unlink(param.get_initrd())

        if kernel is not None:
            os.unlink(param.get_kernel())

        param.set_kernel(None)
        param.set_initrd(None)
        param.cmdline = []
        if type == "xen":
            param.set_bootloader("/usr/bin/pygrub")
        elif type == "kvm":
            param.set_boot_dev("hd")

        if type == "kvm" and iso is not None:
            param.delete_disk("hdc")
        param.set_behavior("on_reboot","restart")
        param.set_behavior("on_crash","restart")

        sync_config_generator(param)

        config = "%s/%s.xml" %(VIRT_XML_CONFIG_DIR,name,)
        if os.path.exists(config):
            f = open(config, "r")
            cfgxml= f.read()
            f.close()
            self._conn.defineXML(cfgxml)

            r_chmod(config,"o-rwx")
            r_chmod(config,"g+rw")
            if os.getuid() == 0:
                r_chgrp(config,KARESANSUI_GROUP)

        try:
            self.search_storage_pools(storage_pool)[0].refresh(0)
        except:
            pass

        return True

    def start_guest(self,name=None):
        """
        <comment-ja>
        ゲストOSの起動を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)

        name = self.guest.get_domain_name()
        config = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR,name,)
        if os.path.exists(config):
            f = open(config, "r")
            cfgxml= f.read()
            f.close()
            self._conn.defineXML(cfgxml)

        self.guest.create()

    def shutdown_guest(self,name=None):
        """
        <comment-ja>
        ゲストOSの停止を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        self.guest.shutdown()

    def reboot_guest(self,name=None):
        """
        <comment-ja>
        ゲストOSを再起動します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        self.guest.reboot()

    def destroy_guest(self,name=None):
        """
        <comment-ja>
        ゲストOSを削除します。(設定ファイルやゲストOS定義は削除されません。)
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        self.guest.destroy()

    def delete_guest(self, name, pool, volume):
        """
        <comment-ja>
        ゲストOSを完全に削除します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        name = self.guest.get_domain_name()
        tmp_pool = self.get_storage_pool_name_bydomain(name, 'os')
        if tmp_pool:
            pool_objs = self.search_kvn_storage_pools(tmp_pool[0])
        else:
            pool_objs = self.search_kvn_storage_pools(pool)

        pool_type = pool_objs[0].get_info()['type']
        if pool_type == 'iscsi':
            domains_dir = VENDOR_DATA_ISCSI_DOMAINS_DIR
            domain_dir = "%s/%s" % (VENDOR_DATA_ISCSI_DOMAINS_DIR, name)
        else:
            domains_dir = self.get_storage_pool_targetpath(pool)
            domain_dir = "%s/%s" % (domains_dir, name)

        vols = self.get_storage_volume_bydomain(name, 'os')
        if vols:
            vol_path = "%s/%s" % (domains_dir, list(vols.keys())[0])
        else:
            vol_path = "%s/%s" % (domains_dir, volume)

        try:
            self.destroy_guest(name)
        except libvirt.libvirtError as e:
            self.logger.info("Could not remove the guest. - name=%s" % name)

        try:
            self.guest.undefine()
        except:
            self.logger.info("Guests definition could not be removed. - name=%s" % name)

        import shutil
        if os.path.islink(vol_path):
            os.unlink(vol_path)

        if os.path.exists(domain_dir):
            #os.removedirs(domain_dir)
            shutil.rmtree(domain_dir)

        # delete qemu snapshot
        domain_snapshot_dir = "%s/%s" % (VIRT_SNAPSHOT_DIR,name,)
        if os.path.exists(domain_snapshot_dir):
            #os.removedirs(domain_snapshot_dir)
            shutil.rmtree(domain_snapshot_dir)

        if tmp_pool:
            try:
                self.search_storage_pools(tmp_pool[0])[0].refresh(0)
            except:
                pass
        else:
            try:
                self.search_storage_pools(pool)[0].refresh(0)
            except:
                pass

    def suspend_guest(self,name=None):
        """
        <comment-ja>
        起動しているゲストOSを一時停止します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        self.guest.suspend()

    def resume_guest(self,name=None):
        """
        <comment-ja>
        suspendしているゲストOSを復帰させます。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        self.guest.resume()

    def autostart_guest(self,flag=None,name=None):
        """
        <comment-ja>
        ゲストOSの自動起動設定を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        guests = self.search_guests(self.guest.get_domain_name())
        if len(guests):
            return self.guest.autostart(flag)
        else:
            return False

    def replicate_storage_volume(self, orig_domname, orig_pool, orig_volume,
                                 dest_domname, dest_pool, dest_volume,
                                 progresscb=None):
        """<comment-ja>
        ストレージボリュームをコピーします。
        @param orig_domname: コピー元ドメイン名
        @param orig_pool: コピー元ストレージプール名
        @param orig_volume: コピー元ストレージボリューム名
        @param dest_domname: コピー先ドメイン名
        @param dest_pool: コピー先ストレージプール名
        @param dest_volume: コピー先ストレージボリューム名
        @param progresscb: コピー方式
        @return: 実行結果
        </comment-ja>
        <comment-en>
        TODO: English Documents(en)
        </comment-en>
        """
        orig_symlink_path = self.get_storage_volume_iscsi_rpath_bystorage(orig_pool, orig_volume)
        orig_rpath = os.path.realpath(orig_symlink_path)
        if not orig_rpath:
            return False

        # orig
        orig_domains_dir = self.get_storage_pool_targetpath(orig_pool)
        orig_domain_dir = "%s/%s" % (orig_domains_dir, orig_domname)

        # dest
        dest_domains_dir = self.get_storage_pool_targetpath(dest_pool)
        dest_domain_dir = self.make_domain_dir(dest_domains_dir, dest_domname)

        orig_files = [orig_rpath,]
        dest_files = ["%s/disk/%s.img" % (dest_domain_dir, dest_volume),]
        if os.path.isfile(dest_files[0]) is True:
            raise KaresansuiVirtException("Already exists in the destination storage volume.")

        if progresscb is not None:
            from karesansui.lib.utils import copy_file_cb
            copy_file_cb(orig_files, dest_files, progresscb, each=False)
        else:
            CopyFile(orig_files, dest_files)

        # symlink
        os.symlink(dest_files[0], "%s/%s" % (dest_domains_dir, dest_volume))

        # Storage Pool refresh
        try:
            self.search_storage_pools(orig_pool)[0].refresh(0)
            self.search_storage_pools(dest_pool)[0].refresh(0)
        except:
            pass

        return True

    def replicate_guest(self, name, source_name, pool, mac=None, uuid=None, graphics=None):
        """<comment-ja>
        ゲストOSのコピーを行います。
        すべてのディスクがfile形式のみ実行可能です。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        param = ConfigParam(name)

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, source_name)
        dom = self._conn.lookupByName(source_name)
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        autostart = False
        try:
            guest_obj = self.search_kvg_guests(source_name)[0]
            if not guest_obj:
                raise KaresansuiVirtException(_("Domain could not be found. name=%s") % source_name)
            autostart = guest_obj.autostart()
        except:
            pass

        # Source storage pool dir
        src_pool = self.get_storage_pool_name_bydomain(source_name, "os")[0]
        src_target_path = self.get_storage_pool_targetpath(src_pool)
        source_disk = "%s/%s/images/%s.img" \
                      % (src_target_path, source_name,source_name)

        pool_dir = self.get_storage_pool_targetpath(pool)
        disk = "%s/%s/images/%s.img" % (pool_dir, name, name)

        # definition for a network interface
        src_interfaces = param.interfaces
        param.interfaces = []
        for ifs in src_interfaces:
            script = ifs['script']
            try:
                model = ifs['model']
            except:
                model = None
            if mac is None:
                mac = GenMAC()
                param.add_interface(mac,"bridge",ifs['bridge'],script,model=model)
            else:
                param.add_interface(mac.lower(),"bridge",ifs['bridge'],script,model=model)
                mac = None

        if uuid is None:
            uuid = StrFromUUID(GenUUID())

        if graphics is None:
            used_ports = self.list_used_graphics_port()
            graphics = NextNumber(GRAPHICS_PORT_MIN_NUMBER,PORT_MAX_NUMBER,used_ports)

        old_disks = param.disks

        # get further informations of disk used by os.
        bus = None
        driver_name = None
        driver_type = None
        for disk_info in old_disks:
            if disk_info['path'] == source_disk:
                try:
                    bus = disk_info['bus']
                except:
                    bus = None
                try:
                    driver_name = disk_info['driver_name']
                except:
                    driver_name = None
                try:
                    driver_type = disk_info['driver_type']
                except:
                    driver_type = None
                break

        param.disks = []
        param.set_uuid(uuid)
        param.set_graphics_port(graphics)
        param.add_disk(disk,
                       self.disk_prefix + "a",
                       bus=bus,
                       driver_name=driver_name,
                       driver_type=driver_type)

        # dest make dirs
        self.make_domain_dir(pool_dir, name)

        # TODO : boot dir

        # 追加ディスクのコピー
        for _disk in old_disks:
            try:
                s_disk_path   = _disk['path']
                s_disk_target = _disk['target']
                s_disk_bus    = _disk['bus']
                try:
                    s_driver_name = _disk['driver_name']
                except:
                    s_driver_name = None
                try:
                    s_driver_type = _disk['driver_type']
                except:
                    s_driver_type = None

                m = re.search("/domains/%s/disk/(?P<disk_name>[0-9\.]+\.img)$" % source_name ,s_disk_path)
                if m:
                    new_disk_path = "%s/%s/disk/%s" % (pool_dir,name,m.group("disk_name"),)

                    param.add_disk(new_disk_path,
                                   s_disk_target,
                                   "disk",
                                   bus=s_disk_bus,
                                   driver_name=s_driver_name,
                                   driver_type=s_driver_type)

                    if not os.path.exists(new_disk_path):
                        CopyFile(s_disk_path,new_disk_path)
            except:
                pass

        # スナップショットのコピー
        # libvirtdの再起動後に認識される。(qemuDomainSnapshotLoad)
        s_domain_snapshot_dir = "%s/%s" % (VIRT_SNAPSHOT_DIR,source_name,)
        if os.path.exists(s_domain_snapshot_dir):
            domain_snapshot_dir = "%s/%s" % (VIRT_SNAPSHOT_DIR,name,)
            for snapshot_xml in glob.glob("%s/*.xml" % s_domain_snapshot_dir):
                snapshot_xml_name = os.path.basename(snapshot_xml)
                new_snapshot_xml = "%s/%s" % (domain_snapshot_dir,snapshot_xml_name,)
                if not os.path.exists(domain_snapshot_dir):
                    os.makedirs(domain_snapshot_dir)

                old_pattern = "<uuid>.{36}</uuid>"
                new_string  = "<uuid>%s</uuid>" % uuid
                file_contents_replace(snapshot_xml,new_snapshot_xml,old_pattern,new_string)
            if os.getuid() == 0:
                if os.path.exists(domain_snapshot_dir):
                    r_chmod(domain_snapshot_dir,"o-rwx")
                    r_chgrp(domain_snapshot_dir,KARESANSUI_GROUP)

                # This is commented out.
                # cos guests that set to autostart flag will be started without intention.
                #from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
                #kvs = KaresansuiVirtSnapshot()
                #kvs.refreshSnapshot()

        try:
            # ゲストOSイメージのコピー
            CopyFile(source_disk,disk)

            # Storage pool directory, OS image set symlink
            os.symlink(disk,
                       "%s/%s" % (pool_dir, uuid))

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)
        except:
            raise

        sync_config_generator(param, name)

        # set autostart flag
        if autostart is True:
            try:
                guest_obj = self.search_kvg_guests(name)[0]
                if not guest_obj:
                    raise KaresansuiVirtException(_("Domain could not be found. name=%s") % name)
                guest_obj.autostart(flag=autostart)
            except:
                raise KaresansuiVirtException(_("Failed to set autostart flag. - dom=%s flag=%s") % (name,autostart))

        # Storage Pool refresh
        for p in [src_pool, pool]:
            try:
                self.search_storage_pools(p)[0].refresh(0)
            except:
                pass

        return True

    def export_guest(self, uuid, name, directory, database, realicon, title="", snapshots=None, progresscb=None):
        """<comment-ja>
        ゲストOSののエクスポートを行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        #inactive_pools = self.list_inactive_storage_pool()
        inactive_pools = []
        active_pools   = self.list_active_storage_pool()

        pool_name = None
        for _pool in inactive_pools + active_pools:
            path = self.search_kvn_storage_pools(_pool)[0].get_info()["target"]["path"]
            if directory == path:
                pool_name = _pool

        if not os.path.exists(directory):
            raise KaresansuiVirtException(_("Directory '%s' not found.") % directory)

        if not (name is None):
            self.guest.set_domain_name(name)

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, name)
        config_file = "%s/%s" % (self.config_dir, name)

        src_pool = self.get_storage_pool_name_bydomain(name, "os")[0]
        src_path = self.get_storage_pool_targetpath(src_pool)

        domain_dir = "%s/%s" % (src_path,name,)
        image_file = "%s/images/%s.img" % (domain_dir,name)
        domain_snapshot_dir = "%s/%s" % (VIRT_SNAPSHOT_DIR,name,)

        export_dir = "%s/%s" % (directory,uuid)
        #export_domain_dir = "%s/%s" % (export_dir,name)
        export_domain_dir = "%s/domain/%s" % (export_dir,name)
        #export_disk_dir = "%s/%s" % (export_dir,name)
        export_disk_dir = "%s/disk" % (export_dir)

        if os.path.exists(export_domain_dir):
            raise KaresansuiVirtException(_("Directory '%s' found.") % export_domain_dir)

        try:
            if not os.path.exists(export_domain_dir):
                os.makedirs(export_domain_dir)
                if os.getuid() == 0:
                    r_chgrp(export_dir,KARESANSUI_GROUP)
                    r_chmod(export_dir,"o-rwx")

            if not os.path.exists(export_disk_dir):
                os.makedirs(export_disk_dir)
                if os.getuid() == 0:
                    r_chgrp(export_dir,KARESANSUI_GROUP)
                    r_chmod(export_dir,"o-rwx")

            # -----------------------
            # Export information to disk to retrieve.
            disk_keys = self.get_storage_volume_bydomain(
                self.guest.get_domain_name(), 'disk', 'key')

            disks_info = []
            for key in list(disk_keys.keys()):
                _volume = key
                _path = disk_keys[key]
                _pool_name = self.get_storage_pool_name_byimage(_path)

                if not _pool_name:
                    raise KaresansuiVirtException("'%s' disk storage pool can not be found." % _volume)
                else:
                    _pool_name = _pool_name[0]

                _pool = self.search_kvn_storage_pools(_pool_name)
                if not _pool:
                    raise KaresansuiVirtException("'%s' disk storage pool(path) can not be found." % _volume)
                else:
                    _pool = _pool[0]

                _pool_path = _pool.get_info()['target']['path']
                pool_uuid = _pool.get_info()['uuid']

                disks_info.append({"volume" : _volume,
                                   "volume_path" : _path,
                                   "pool_name" : _pool_name,
                                   "domname" : self.guest.get_domain_name(),
                                   "pool_path" : _pool_path,
                                   "pool_uuid" : pool_uuid
                                   })

            # Disk export
            for disk_info in disks_info:
                disk_dir = "%s/%s" % (disk_info["pool_path"], disk_info["domname"])
                if progresscb is not None:
                    from karesansui.lib.utils import copy_file_cb

                    src_files = []
                    dst_files = []
                    for _sub in glob.glob("%s/disk/*" % disk_dir):
                        if os.path.isfile(_sub):
                            # {export uuid}/disk/{pool name}/{domname}/[images|boot|disk]
                            #dst_file = "%s/%s" % (export_disk_dir, os.path.basename(_sub),)
                            dst_file = "%s/%s/%s/disk/%s" % (export_disk_dir,
                                                       disk_info["pool_name"],
                                                       disk_info["domname"],
                                                       os.path.basename(_sub),
                                                       )
                            src_file = _sub
                            src_files.append(src_file)
                            dst_files.append(dst_file)
                    copy_file_cb(src_files,dst_files,progresscb,each=False)
                else:
                    CopyFile(disk_dir, export_disk_dir)

            # -----------------------

            # copy domain image data
            if progresscb is not None:
                from karesansui.lib.utils import copy_file_cb

                src_files = []
                dst_files = []
                # os image
                src_files.append("%s/images/%s.img" % (domain_dir, name))
                dst_files.append("%s/images/%s.img" % (export_domain_dir, name))
                copy_file_cb(src_files,dst_files,progresscb,each=False)

                # boot
                src_files = []
                dst_files = []
                for _sub in glob.glob("%s/boot/*" % domain_dir):
                    if os.path.isfile(_sub) is True:
                        dst_file = "%s/boot/%s" % (export_domain_dir,os.path.basename(_sub),)
                        src_files.append(_sub)
                        dst_files.append(dst_file)

                copy_file_cb(src_files,dst_files,progresscb,each=False)
            else:
                CopyFile(domain_dir,export_domain_dir)

            # copy domain configuration
            export_xml_file    = "%s/%s.xml"  % (export_dir,name,)
            CopyFile(xml_file,   export_xml_file)
            export_config_file = "%s/%s.conf" % (export_dir,name,)
            CopyFile(config_file,export_config_file)

            # copy snapshot xmls
            if os.path.exists(domain_snapshot_dir):
                export_snapshot_dir = "%s/snapshot" % (export_domain_dir,)

                try:
                    os.makedirs(export_snapshot_dir)
                except:
                    pass

                for snapshot_xml in glob.glob("%s/*.xml" % domain_snapshot_dir):
                    snapshot_xml_name = os.path.basename(snapshot_xml)
                    export_snapshot_xml = "%s/%s" % (export_snapshot_dir,snapshot_xml_name,)
                    CopyFile(snapshot_xml,export_snapshot_xml)

            # symlink to recognize as libvirt pool
            export_image_file = "%s/images/%s.img" % (export_domain_dir,name)
            link_file = "%s/%s-%s.img" % (directory,uuid,name,)
            if os.path.exists(link_file) is False:
                os.symlink(export_image_file,link_file)

            # web icon image
            if database['icon']:
                CopyFile(realicon, "%s/%s" % (export_dir, database['icon']))

            # info.dat
            param = ExportConfigParam()

            param.set_path("%s/%s" % (export_dir, GUEST_EXPORT_FILE))
            param.set_uuid(uuid)
            param.set_domain(name)
            param.set_title(title)
            param.set_created(str(int(time.time())))
            param.set_database(database)
            param.set_pool(src_pool)
            param.set_snapshots(snapshots)

            # add_disk
            for disk_info in disks_info:
                param.add_disk(disk_info['volume'],
                               disk_info['pool_name'],
                               disk_info['pool_path'],
                               )

            generator = ExportXMLGenerator(param.get_path())
            try:
                cfgxml = generator.generate(param)
            except:
                raise
            generator.writecfg(cfgxml)

            if os.getuid() == 0:
                r_chgrp(export_dir,KARESANSUI_GROUP)
                r_chmod(export_dir,"o-rwx")

            if pool_name is not None:
                try:
                    self.search_storage_pools(pool_name)[0].refresh(0)
                except:
                    pass

        except:
            raise

    def import_guest(self, directory, uuid, progresscb):
        """
        <comment-ja>
        ゲストOSのインポートを行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not os.path.exists(directory):
            raise KaresansuiVirtException(_("Directory '%s' not found.") % directory)

        export_dir = directory

        # read info.dat
        param = ExportConfigParam()
        info_file = "%s/info.dat" % (export_dir,)
        if os.path.exists(info_file):
            try:
                param.load_xml_config(info_file)
            except:
                raise KaresansuiVirtException(_("'%s' is invalid format.") % info_file)
        else:
            raise KaresansuiVirtException(_("'%s' not found.") % info_file)

        id    = param.get_uuid()
        name  = param.get_domain()
        title = param.get_title()
        created = param.get_created()

        domains_dir = self.get_storage_pool_targetpath(param.get_pool())
        xml_file    = "%s/%s.xml"        % (VIRT_XML_CONFIG_DIR, name)
        config_file = "%s/%s"            % (self.config_dir, name)
        domain_dir  = "%s/%s"            % (domains_dir,name,)
        image_file  = "%s/images/%s.img" % (domain_dir,name)
        domain_snapshot_dir = "%s/%s"    % (VIRT_SNAPSHOT_DIR,name,)

        export_domain_dir   = "%s/domain/%s"       % (export_dir,name,)
        #export_snapshot_dir = "%s/snapshot" % (export_domain_dir,)
        export_snapshot_dir = "%s/snapshot" % (export_domain_dir)

        if not os.path.exists(export_domain_dir):
            raise KaresansuiVirtException(_("Directory '%s' not found.") % export_domain_dir)

        if os.path.exists(domain_dir):
            raise KaresansuiVirtException(_("guest '%s' already exists.") % name)

        try:
            from karesansui.lib.utils import copy_file_cb
            # copy disks {export dir}/{export uuid}/disk/{pool}/{domname}/disk/{disk uuid}.img
            export_disk_dir = "%s/disk" % (export_dir)
            export_disks = param.get_disks()
            src_files = []
            dst_files = []
            dst_symlinks = []
            for disk in export_disks:
                volume = disk['uuid']
                pool_name = disk['name']
                pool_path = disk['path']
                pool = self.search_kvn_storage_pools(pool_name)
                if not pool:
                    raise KaresansuiVirtException(_("Disk storage pools were found to import. - pool=%s") \
                                            % pool_name)
                else:
                    pool = pool[0]

                # check
                if pool_path != pool.get_json()['target']['path']:
                    raise KaresansuiVirtException(_("When exporting, there are differences in the storage pool information. (Storage pool path) = export=%s, import=%s") \
                                            % (pool_path, pool.get_json()['target']['path']))

                src_file = "%s/%s/%s/disk/%s.img" % (export_disk_dir, pool_name, name, volume)
                if os.path.isfile(src_file) is False:
                    raise KaresansuiVirtException(_("Could not find the exported disk image. src_file=%s", src_file))

                dst_file = "%s/%s/disk/%s.img" % (pool.get_json()['target']['path'], name, volume)

                src_files.append(src_file)
                dst_files.append(dst_file)
                dst_symlinks.append("%s/%s" % (pool.get_json()['target']['path'], volume))

            copy_file_cb(src_files,dst_files,progresscb,each=False)
            for i in range(len(dst_symlinks)):
                os.symlink(dst_files[i], dst_symlinks[i])


            # copy domain image data
            src_files = []
            dst_files = []
            for _sub in glob.glob("%s/*" % export_domain_dir):
                if os.path.isdir(_sub):
                    dst_dir = "%s/%s" % (domain_dir,os.path.basename(_sub),)
                    for _sub2 in glob.glob("%s/*" % _sub):
                        if os.path.isfile(_sub2):
                            src_file = _sub2
                            dst_file = "%s/%s" % (dst_dir,os.path.basename(_sub2),)
                            src_files.append(src_file)
                            dst_files.append(dst_file)
            copy_file_cb(src_files,dst_files,progresscb,each=False)

            export_xml_file    = "%s/%s.xml"  % (export_dir,name,)
            # os image symlink
            g_param = ConfigParam(name)
            if os.path.isfile(export_xml_file) is False:
                raise KaresansuiVirtException(
                    _("Export data not found. - path=%s" % export_xml_file))
            g_param.load_xml_config(export_xml_file)

            os_image_path = "%s/%s/images/%s.img" % (domains_dir, name, name)
            if os.path.isfile(os_image_path) is False:
                raise KaresansuiVirtException(_("Failed to import guest image. Image not found.- path=%s") \
                                              % os_image_path)
            os.symlink(os_image_path, "%s/%s" % (domains_dir, g_param.uuid))

            # copy domain configuration
            export_config_file = "%s/%s.conf" % (export_dir,name,)
            if uuid is None:
                CopyFile(export_xml_file    ,xml_file)
                CopyFile(export_config_file ,config_file)
            else:
                old_pattern = "<uuid>.{36}</uuid>"
                new_string  = "<uuid>%s</uuid>" % uuid
                file_contents_replace(export_xml_file,xml_file,old_pattern,new_string)
                old_pattern = "^uuid = .*"
                new_string  = "uuid = '%s'" % str(uuid)
                file_contents_replace(export_config_file ,config_file,old_pattern,new_string)

            if os.path.exists(xml_file):
                self._conn.defineXML("".join(ConfigFile(xml_file).read()))

            # copy snapshot xmls
            # libvirtdの再起動後に認識される。(qemuDomainSnapshotLoad)
            if os.path.exists(export_snapshot_dir):

                if not os.path.exists(domain_snapshot_dir):
                    os.makedirs(domain_snapshot_dir)

                for snapshot_xml in glob.glob("%s/*.xml" % export_snapshot_dir):
                    snapshot_xml_name = os.path.basename(snapshot_xml)
                    new_snapshot_xml = "%s/%s" % (domain_snapshot_dir,snapshot_xml_name,)
                    CopyFile(snapshot_xml,new_snapshot_xml)


            if os.getuid() == 0:
                r_chgrp(domain_dir,KARESANSUI_GROUP)
                r_chmod(domain_dir,"o-rwx")
                r_chgrp(xml_file,    KARESANSUI_GROUP)
                r_chgrp(config_file, KARESANSUI_GROUP)
                if os.path.exists(domain_snapshot_dir):
                    r_chmod(domain_snapshot_dir,"o-rwx")
                    r_chgrp(domain_snapshot_dir,KARESANSUI_GROUP)

                # This is commented out.
                # cos guests that set to autostart flag will be started without intention.
                #from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
                #kvs = KaresansuiVirtSnapshot()
                #kvs.refreshSnapshot()

            # Storage Pool refresh
            try:
                self.search_storage_pools(param.get_pool())[0].refresh(0)
                for disk in param.get_disks():
                    self.search_storage_pools(disk["name"])[0].refresh(0)
            except:
                pass

        except:
            raise

    def get_hypervisor_type_bydomain(self,name=None):
        """<comment-ja>
        指定ドメインのハイパーバイザーの種類を取得する。
        @param void
        @return: hypervisor type
                 xen or kvm is available now (but depend on domain.xml)
                 e.g. xen kvm hyperv kqemu ldom lxc one openvz phyp qemu test
                      uml vbox vmware vserver
        @rtype: string (lower case only)
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        retval = None

        if not (name is None):
            self.guest.set_domain_name(name)

        try:
            retval = self.guest.get_info()['VMType']
        except libvirt.libvirtError as e:
            pass

        return retval

    """
    Network
    """
    def list_inactive_network(self):
        """
        <comment-ja>
        現在起動していない仮想ネットワークのリストを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        return self._conn.listDefinedNetworks()

    def list_active_network(self):
        """
        <comment-ja>
        現在起動している仮想ネットワークのリストを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        names = []
        for name in self._conn.listNetworks():
            names.append(name)
        return names

    def search_networks(self, name=None):
        """
        <comment-ja>
        仮想ネットワークの検索を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        networks = []

        names = self._conn.listNetworks()
        for __name in names:
            networks.append(self._conn.networkLookupByName(__name))
        names = self.list_inactive_network()
        for __name in names:
            networks.append(self._conn.networkLookupByName(__name))

        if name == None:
            return networks

        regex_regex = re.compile(r"""^regex:(?P<regex>.*)""")
        m = regex_regex.match(name)

        n_networks = []
        for network in networks:
            network_name = network.name()
            if m == None:
                if network_name == name:
                    return [network]
            else:
                regex = m.group('regex')
                query_regex = re.compile(r""+regex+"")
                n = query_regex.search(network_name)
                if n != None:
                    n_networks.append(network)
        if len(n_networks):
            return n_networks

        #return []
        raise KaresansuiVirtException("network %s not found" % name)

    def search_kvn_networks(self, name=None):
        """<comment-ja>
        指定された仮想ネットワークオブジェクトをKaresansuiVirtNetworkオブジェクトのlistにして返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        if is_uuid(name):
            name = self.uuid_to_domname(name)

        networks = []
        for network in self.search_networks(name):
            networks.append(
                KaresansuiVirtNetwork(conn=self, name=network.name()))

        return networks

    def create_network(self, name, cidr, dhcp_start=None, dhcp_end=None, forward=None, bridge=None, autostart=None):
        """
        <comment-ja>
        仮想ネットワークを作成します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        param = NetworkConfigParam(name)
        param.set_default_networks(cidr,dhcp_start,dhcp_end)
        param.set_ipaddr_and_netmask(cidr)
        if forward:
            if 'dev' in list(forward.keys()):
                param.set_forward_dev(forward['dev'])
            if 'mode' in list(forward.keys()):
                param.set_forward_mode(forward['mode'])
        if bridge:
            param.set_bridge(bridge)
        uuid = StrFromUUID(GenUUID())
        param.set_uuid(uuid)

        generator = NetworkXMLConfigGenerator()
        try:
            cfgxml = generator.generate(param)
        except:
            raise
        generator.writecfg(cfgxml)

        ret = libvirtmod.virNetworkCreateXML(self._conn._o,cfgxml)
        time.sleep(2)
        self._conn.networkDefineXML(cfgxml)

        filename = "%s/%s.xml" %(VIRT_NETWORK_CONFIG_DIR,name)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

        if autostart is not None:
            self.network.set_network_name(name)
            self.network.autostart(autostart)

        return ret

    def update_network(self, name, cidr=None, dhcp_start=None, dhcp_end=None, forward=None, bridge=None, autostart=None):
        """
        <comment-ja>
        仮想ネットワークを更新します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        # パラメータをリセットする場合と引数が無い場合の区別 => リセットの場合は、空文字列を渡す。

        if not ( cidr or
                 dhcp_start or
                 dhcp_end or
                 forward or
                 bridge ):
            # Not changed, do nothing
            # 更新成功時と同じ返り値(0)を返す
            return 0

        try:
            param  = self.search_kvn_networks(name)[0].get_network_config_param()
        except:
            raise KaresansuiVirtException("Can't get parameters of network '%s'." % name)

        if cidr:
            param.set_ipaddr_and_netmask(cidr)
        if dhcp_start:
            param.set_dhcp_start(dhcp_start)
        if dhcp_end:
            param.set_dhcp_end(dhcp_end)
        if forward:
            if 'dev' in list(forward.keys()):
                if forward['dev'] == '':
                    param.set_forward_dev(None)
                else:
                    param.set_forward_dev(forward['dev'])
            if 'mode' in list(forward.keys()):
                if forward['mode'] == '':
                    param.set_forward_mode(None)
                else:
                    param.set_forward_mode(forward['mode'])
        if bridge:
            param.set_bridge(bridge)

        generator = NetworkXMLConfigGenerator()
        try:
            cfgxml = generator.generate(param)
        except:
            raise

        self.stop_network(name)

        generator.writecfg(cfgxml)

        ret = libvirtmod.virNetworkCreateXML(self._conn._o,cfgxml)
        time.sleep(2)
        self._conn.networkDefineXML(cfgxml)

        if autostart is not None:
            self.network.autostart(autostart)

        return ret

    def start_network(self,name=None):
        """
        <comment-ja>
        仮想ネットワークを起動します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.network.set_network_name(name)
        self.network.start()

    def stop_network(self,name=None):
        """
        <comment-ja>
        仮想ネットワークを停止します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.network.set_network_name(name)
        self.network.stop()

    def delete_network(self,name=None):
        """
        <comment-ja>
        仮想ネットワークを削除します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        self.stop_network(name)
        if len(self.search_networks(name)) > 0:
            self.network.undefine()

        config = "%s/%s.xml" %(VIRT_NETWORK_CONFIG_DIR, self.network.get_network_name())
        if os.path.exists(config):
            os.unlink(config)

        config = "%s/autostart/%s.xml" %(VIRT_NETWORK_CONFIG_DIR, self.network.get_network_name())
        if os.path.exists(config):
            os.unlink(config)

    def autostart_network(self,flag=None,name=None):
        """
        <comment-ja>
        仮想ネットワークの自動起動を設定します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.guest.set_domain_name(name)
        networks = self.search_networks(self.network.get_network_name())
        if len(networks):
            return self.network.autostart(flag)
        else:
            return False


    """
    Storage Pool
    """
    def refresh_pools(self):
        """
        <comment-ja>
        現在のストレージプール情報をリフレッシュします。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        # refresh pool.
        active_pools =  self.list_active_storage_pool()
        #inactive_pools =  self.list_inactive_storage_pool()
        inactive_pools = []
        for pool_name in active_pools + inactive_pools:
            try:
                pool =  self.search_kvn_storage_pools(pool_name)
                path = pool[0].get_info()["target"]["path"]
                self.search_storage_pools(pool_name)[0].refresh(0)
            except:
                pass
    
    def list_inactive_storage_pool(self):
        """
        <comment-ja>
        現在起動していないストレージプールのリストを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        pools = self._conn.listDefinedStoragePools()
        ret = []
        for i in range(len(pools)):
            path = "%s/%s.xml" % (VIRT_STORAGE_CONFIG_DIR, pools[i])
            if os.path.isfile(path) is False:
                continue
            ret.append(pools[i])
        return ret

    def list_active_storage_pool(self):
        """
        <comment-ja>
        現在起動しているストレージプールのリストを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        names = []
        for name in self._conn.listStoragePools():
            names.append(name)
        return names

    def search_storage_pools(self, name=None, active_only=False):
        """
        <comment-ja>
        ストレージプールの検索を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        pools = []

        names = self._conn.listStoragePools()
        for __name in names:
            pools.append(self._conn.storagePoolLookupByName(__name))

        if active_only is False:
            names = self.list_inactive_storage_pool()
            for __name in names:
                pools.append(self._conn.storagePoolLookupByName(__name))

        if name == None:
            return pools

        regex_regex = re.compile(r"""^regex:(?P<regex>.*)""")
        m = regex_regex.match(name)

        n_pools = []
        for pool in pools:
            pool_name = pool.name()
            if m == None:
                if pool_name == name:
                    return [pool]
            else:
                regex = m.group('regex')
                query_regex = re.compile(r""+regex+"")
                n = query_regex.search(storage_name)
                if n != None:
                    n_pools.append(pool)
        if len(n_pools):
            return n_pools

        #return []
        raise KaresansuiVirtException("Storage pool %s not found" % name)

    def search_kvn_storage_pools(self, name=None, active_only=False):
        """<comment-ja>
        指定されたStorage Pool をKaresansuiVirtStoragePoolオブジェクトのlistにして返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        if is_uuid(name):
            name = self.uuid_to_domname(name)

        pools = []
        for pool in self.search_storage_pools(name, active_only):
            pools.append(
                KaresansuiVirtStoragePool(conn=self, name=pool.name()))

        return pools

    def start_storage_pool(self, name):
        """
        <comment-ja>
        ストレージプールの起動します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        return self.storage_pool.create(name)
        
    def create_storage_pool(self, name, type,
                            target_path=None,
                            allocation=0, available=0, capacity=0,
                            source_f_type=None, source_dev_path=None, source_a_name=None,
                            source_dir_path=None, source_h_name=None,
                            target_p_group=None, target_p_label=None,
                            target_p_mode=None, target_p_owner=None,
                            target_e_format=None, target_encryption_s_type=None,
                            #target_encryption_s_uuid=None,
                            ):
        """
        <comment-ja>
        ストレージプールの作成を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """

        param = StoragePoolConfigParam(name)
        
        uuid = StrFromUUID(GenUUID())
        param.set_uuid(uuid)

        if type is not None:
            param.set_pool_type(type)

        if target_path is not None:
            param.set_target_path(target_path)

        param.set_allocation(allocation)
        param.set_available(available)
        param.set_capacity(capacity)
        
        if source_f_type is not None:
            param.set_source_f_type(source_f_type)

        if source_dev_path is not None:
            param.set_source_dev_path(source_dev_path)

        if source_dir_path is not None:
            param.set_source_dir_path(source_dir_path)

        if source_f_type is not None:
            param.set_source_f_type(source_f_type)

        if source_h_name is not None:
            param.set_source_h_name(source_h_name)

        if target_e_format is not None and \
               target_encryption_s_type is not None:
            param.set_target_e_format(target_e_format)
            param.set_target_encryption_s_type(target_encryption_s_type)
            target_encryption_s_uuid = StrFromUUID(GenUUID())
            param.set_target_encryption_s_uuid(target_encryption_s_uuid)

        if target_p_group is not None:
            param.set_target_permissions_group(target_p_group)

        if target_p_label is not None:
            param.set_target_permissions_label(target_p_label)

        if target_p_mode is not None:
            param.set_target_permissions_mode(target_p_mode)

        if target_p_owner is not None:
            param.set_target_permissions_owner(target_p_owner)

        generator = StoragePoolXMLConfigGenerator()
        try:
            cfgxml = generator.generate(param)
        except:
            raise
        generator.writecfg(cfgxml)

        if self.storage_pool.start(cfgxml, 0, name) == 0:
            return True
        else:
            return False

    def is_autostart_storage_pool(self, name=None):
        """
        <comment-ja>
        指定されたストレージプールが自動起動するか。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.storage_pool.set_storage_name(name)

        pools = self.search_storage_pools(self.storage_pool.get_storage_name())
        if len(pools):
            ret = self.storage_pool.autostart()
            if ret == 0:
                return False # OFF
            elif ret == 1:
                return True # ON
            else:
                return None # ERR
        else:
            return None # ERR
        
    def autostart_storage_pool(self, flag=None, name=None):
        """
        <comment-ja>
        ストレージプールの自動起動設定を行います。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if not (name is None):
            self.storage_pool.set_storage_name(name)

        pools = self.search_storage_pools(self.storage_pool.get_storage_name())
        if len(pools):
            if self.storage_pool.set_autostart(flag) == 0:
                return True
            else:
                return False
        else:
            return False

    def destroy_storage_pool(self,name=None):
        """
        <comment-ja>
        ストレージプールの削除を行います。(設定ファイルなどの情報は削除されません)
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if name is not None:
            self.storage_pool.set_storage_name(name)
        if self.storage_pool.destroy() == 0:
            return True
        else:
            return False

    def delete_storage_pool(self,name=None, flags=False):
        """
        <comment-ja>
        ストレージプールを完全に削除します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if name is not None:
            self.storage_pool.set_storage_name(name)

        # autostart off
        self.autostart_storage_pool(False)

        path = "%s/%s.xml" % (VIRT_STORAGE_CONFIG_DIR, self.storage_pool.get_storage_name())
        if os.path.isfile(path) is True:
            os.unlink(path)

        mode = VIR_STORAGE_POOL_DELETE_NORMAL
        if flags is True:
            mode = VIR_STORAGE_POOL_DELETE_ZEROED

        if self.storage_pool.delete(mode) == 0:
            return True
        else:
            return False

    def is_used_storage_pool(self, name=None, active_only=False):
        """
        <comment-ja>
        ストレージプールが現在利用されているか。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        if name is None:
            return False

        guests = self.list_active_guest()
        if active_only is False:
            guests += self.list_inactive_guest()

        pools = []
        for guest in guests:
            pools += self.get_storage_pool_name_bydomain(guest)

        if name in pools:
            return True

        return False

    def is_storage_volume(self, path):
        """<comment-ja>
        指定したパスがストレージボリュームに含まれているか。
        </comment-ja>
        <comment-en>
        Storage volume that contains the specified path.
        </comment-en>
        """
        if os.path.isfile(path) is False:
            return False

        try:
            vir_storage_vol = self.storage_volume._conn.storageVolLookupByPath(path)
            return True
        except libvirt.libvirtError as e:
            # _("The specified path is not registered in the storage volume. '%s' (%s)")
            return False

    def get_storage_volume(self, pool_name, vol_name):
        """
        <comment-ja>
        ストレージボリュームを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        vol = None

        try:
            pools = self.search_storage_pools(pool_name)
            if len(pools) <= 0:
                return vol
            if vol_name in pools[0].listVolumes():
                vol = pools[0].storageVolLookupByName(vol_name)
        except libvirt.libvirtError as e:
            return vol

        return vol

    def get_storage_volume_path(self, pool_name, vol_name):
        """
        <comment-ja>
        ストレージボリュームのパスを取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        try:
            vol = self.get_storage_volume(pool_name, vol_name)
            if vol is None:
                return None
            vol_path = vol.path()
            return vol_path
        except libvirt.libvirtError as e:
            return None

    def get_storage_pool_UUIDString2kvn_storage_pool(self, uuidstr):
        """
        <comment-ja>
        ストレージプールのUUIDをもとに、ストレージプール情報を取得します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        pool_obj = self._conn.storagePoolLookupByUUIDString(uuidstr)
        return self.search_kvn_storage_pools(pool_obj.name())
        
    def create_storage_volume(self,
                              name,
                              pool_name,
                              t_f_type,
                              use,
                              volume_name=None,
                              #t_path=None,
                              key=None, allocation=0, capacity=0, c_unit=None,
                              source=None,
                              t_p_owner=None,t_p_group=None,t_p_mode=None, t_p_label=None,
                              b_path=None,
                              b_format=None,
                              b_p_owner=None, b_p_group=None, b_p_mode=None, b_p_label=None):
        """
        <comment-ja>
        ストレージボリュームを作成します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        param = StorageVolumeConfigParam(name)

        if volume_name is None:
            uuid = StrFromUUID(GenUUID())
        else:
            uuid = volume_name
        param.set_uuid(uuid)
        param.set_storage_name(uuid)

        self.storage_pool.set_storage_name(pool_name)
        self.storage_volume.set_storage_volume_name(uuid)

        #if t_path is not None:
        #   param.set_target_path(t_path)

        param.set_target_f_type(t_f_type)

        if key is not None:
            set_key(key)

        param.set_allocation(allocation)
        param.set_capacity(capacity)

        if c_unit is not None and (capacity != 0 or allocation != 0):
            param.set_c_unit(c_unit)

        if source is not None:
            param.set_source(source)
                
        if t_p_owner is not None:
            param.set_target_permissions_owner(t_p_owner)

        if t_p_group is not None:
            param.set_target_permissions_group(t_p_group)

        if t_p_mode is not None:
            param.set_target_permissions_mode(t_p_mode)

        if t_p_label is not None:
            param.set_target_permissions_label(t_p_label)

        if b_path is not None:
            param.set_backingStore_path(b_path)
            if b_format is not None:
                param.set_backingStore_format(b_format)

            if b_p_owner is not None:
                param.set_backingStore_permissions_owner(b_p_owner)

            if b_p_group is not None:
                param.set_backingStore_permissions_group(b_p_group)

            if b_p_mode is not None:
                param.set_backingStore_permissions_mode(b_p_mode)

            if b_p_label is not None:
                param.set_backingStore_permissions_label(b_p_label)

        generator = StorageVolumeXMLConfigGenerator()
        try:
            cfgxml = generator.generate(param)
        except:
            raise

        # comment out
        #generator.writecfg(cfgxml)

        vir_storage_vol = self.storage_pool.vol_createXML(cfgxml, 0)

        if not isinstance(vir_storage_vol, libvirt.virStorageVol):
            return False
        # storage dir
        pool_objs = self.search_kvn_storage_pools(pool_name)
        if not pool_objs:
            raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                          pool_name)

        # TODO iscsi block device
        domains_dir = pool_objs[0].get_info()["target"]["path"]
        domain_dir = self.make_domain_dir(domains_dir, name)

        import shutil
        if use == DISK_USES["IMAGES"]:
            disk = "%s/%s/%s.img" % (domain_dir, DISK_USES["IMAGES"], name)
            shutil.move("%s/%s" % (domains_dir, param.get_storage_name()),
                        disk)

            os.symlink(disk,
                       "%s/%s" % (domains_dir, param.get_storage_name()))
        else:
            disk = "%s/%s/%s.img" % (domain_dir, DISK_USES["DISK"], uuid)
            shutil.move("%s/%s" % (domains_dir, uuid),
                        disk)

            os.symlink(disk,
                       "%s/%s" % (domains_dir, uuid))

        # Storage Pool refresh
        try:
            self.search_storage_pools(pool_name)[0].refresh(0)
        except:
            pass

        return True

    def delete_storage_volume(self,pool_name, vol_name, use, flags=False):
        """
        <comment-ja>
        ストレージボリュームを完全に削除します。
        </comment-ja>
        <comment-en>
        TODO:
        </comment-en>
        """
        self.storage_volume.set_storage_name(pool_name)
        self.storage_volume.set_storage_volume_name(vol_name)

        # delete storage dir
        pool_objs = self.search_kvn_storage_pools(pool_name)
        if not pool_objs:
            raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                              pool_name)

        domains_dir = pool_objs[0].get_info()["target"]["path"]
        target_path = "%s/%s" % (domains_dir, vol_name)
        taget_real_path = os.path.realpath(target_path)

        # delete process
        mode = VIR_STORAGE_VOL_DELETE_NORMAL
        if flags is True:
            mode = VIR_STORAGE_VOL_DELETE_ZEROED

        if self.storage_volume.delete(mode) != 0:
            return False

        # physical process
        if use == DISK_USES["IMAGES"]:
            os.remove(taget_real_path)
            if os.path.exists(target_path) is True:
                os.remove(target_path)
        elif use == DISK_USES["DISK"]:
            os.remove(taget_real_path)
            if os.path.exists(target_path) is True:
                os.remove(target_path)
        else:
            pass

    def get_storage_pool_type(self, pool_name):
        """<comment-ja>
        ストレージプールのタイプを取得する
        @param pool_name: ストレージプール名
        @return: ストレージプールの種別
        @rtype: string
        </comment-ja>
        <comment-en>
        Get the type of storage pool.
        @param pool_name: name of storage pool
        @return: type of storage pool
        @rtype: string
        </comment-en>
        """
        retval = None

        try:
            pool_objs = self.search_kvn_storage_pools(pool_name)
            if not pool_objs:
                raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                          pool_name)
            retval = pool_objs[0].get_info()['type']
        except:
            pass

        return retval

    def get_storage_pool_targetpath(self, pool_name):
        """<comment-ja>
        ストレージプールのターゲットパスを取得します。(dir)
        @param pool_name: ストレージプール名
        @return: ターゲットパス
        @rtype: string
        </comment-ja>
        <comment-en>
        Get the target path of storage pool.
        @param pool_name: name of storage pool
        @return: target path
        @rtype: string
        </comment-en>
        """
        retval = None

        try:
            pool_objs = self.search_kvn_storage_pools(pool_name)
            if not pool_objs:
                raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                          pool_name)
            retval = pool_objs[0].get_info()['target']['path']
        except:
            pass

        return retval

    def get_storage_pool_sourcedevicepath(self, pool_name):
        """<comment-ja>
        ストレージプールのソースデバイスパスを取得します。(iscsi)
        @param pool_name: ストレージプール名
        @return: ソースデバイスパス
        @rtype: string
        </comment-ja>
        <comment-en>
        Get the source device path of storage pool.
        @param pool_name: name of storage pool
        @return: source device path
        @rtype: string
        </comment-en>
        """
        retval = None

        try:
            pool_objs = self.search_kvn_storage_pools(pool_name)
            if not pool_objs:
                raise KaresansuiVirtException(_("Storage pool could not be found. pool=%s") % \
                                          pool_name)
            retval = pool_objs[0].get_info()['source']['dev_path']
        except:
            pass

        return retval

    def get_storage_pool_name_byimage(self, path):
        """<comment-ja>
        ディスクイメージのパスからストレージプールの名前を取得する
        @param path: ディスクイメージのパス
        @return: ストレージプールの名前
        @rtype: list
        </comment-ja>
        <comment-en>
        Get name of storage pool where the specified disk image belongs to.
        @param path: path of disk image
        @return: list of storage pool name
        @rtype: list
        </comment-en>
        """
        retval = []

        paths = [path]
        realpath = os.path.realpath(path)

        # Includes realpath as detecting target if it is symbolic link.
        if realpath != path:
            paths.append(realpath)

        try:
            pool_objs = self.search_kvn_storage_pools()
            if not pool_objs:
                raise KaresansuiVirtException(_("No storage pools could be found."))

            for pool_obj in pool_objs:
                pool_info = pool_obj.get_info()
                name        = pool_info['name']
                pool_type   = pool_info['type']

                for vol_name,vol_path in self.get_storage_volume_bypool(name, attr="path").items():
                    for _path in paths:
                        if pool_type == "dir":
                            if ( vol_path == _path or os.path.realpath(vol_path) == _path ) and not name in retval:
                                retval.append(name)
                        else:
                            if ( vol_path == _path[0:len(vol_path)] ) and not name in retval:
                                retval.append(name)

        except:
            pass

        return retval

    def get_storage_pool_name_bydomain(self, domain, image_type=None):
        """<comment-ja>
        ドメインの名前からストレージプールの名前を取得する
        * iscsi is returning the [].
        @param domain: ドメイン名
        @param image_type: イメージの種別 
                     "os"                :ゲストOS本体のイメージファイル
                     "disk"              :拡張ディスクのイメージファイル
                     未指定またはそれ以外:ドメインに属する全てのイメージファイル
        @return: ストレージプールの名前
        @rtype: list
        </comment-ja>
        <comment-en>
        Get name of storage pool where image files that the specified domain uses belong to.

        @param domain: domain name
        @return: list of storage pool name
        @rtype: list
        </comment-en>
        """
        retval = []

        regex = []
        if image_type == "os":
            regex.append("%s/images/%s\.img$" % (domain,domain,))
        if image_type == "disk":
            regex.append("%s/disk/[0-9\.]+\.img$" % (domain,))
        regex_str = "|".join(regex)

        try:
            guest_obj = self.search_kvg_guests(domain)[0]
            if not guest_obj:
                raise KaresansuiVirtException(_("Domain could not be found. name=%s") % \
                                          domain)

            os_root = guest_obj.get_info()['os_root']

            for info in guest_obj.get_disk_info():
                try:
                    target = info['target']['dev']
                except:
                    target = None

                try:
                    source = info['source']['file']
                except:
                    try:
                        source = info['source']['dev']
                    except:
                        source = None

                pools = []
                if image_type == "os":
                   if os_root is not None and target == os.path.basename(os_root):
                       pools = self.get_storage_pool_name_byimage(source)
                elif image_type == "disk":
                   if os_root is not None and target != os.path.basename(os_root):
                       pools = self.get_storage_pool_name_byimage(source)
                else:
                    pools = self.get_storage_pool_name_byimage(source)

                if len(pools) > 0:
                    for pool_name in pools:
                        if not pool_name in retval:
                            retval.append(pool_name)

            # in case that os_root is not specified.
            if len(retval) == 0:
                for info in guest_obj.get_disk_info():
                    if re.search(regex_str,info['source']['file']):
                        for pool_name in self.get_storage_pool_name_byimage(info['source']['file']):
                            if not pool_name in retval:
                                retval.append(pool_name)

        except:
            pass

        return retval


    def get_storage_volume_bypool(self, pool, attr="name"):
        """<comment-ja>
        ストレージプールの名前からボリュームの一覧を取得する
        @param pool: プール名
        @param attr: 取得する属性
                     "name"  :ボリュームの名前(UUID形式)
                     "key"   :ボリュームのキー
                     "path"  :ボリュームのパス
                     "info"  :ボリュームの情報
                     未指定  :nameが指定されたものとする

                     attr 'info' depends on virStorageVolInfo structure.
                       int type;                      virStorageVolType flags
                                                      0 :Regular file
                                                      1 :Block
                       unsigned long long capacity;   Logical size bytes
                       unsigned long long allocation; Current allocation bytes
        @return: ストレージボリューム名と対応するデータの辞書配列
        @rtype: dict
        </comment-ja>
        <comment-en>
        Get name of storage volume in the specified pool.
        
        @param pool: name of pool
        @param attr: volume attribute that you want to get
                     "name"  :name of volume (UUID style)
                     "key"   :key of volume
                     "path"  :path of volume
                     "info"  :volume information
                     none    :same as 'name' is specified

        @return: dict of storage volume
        @rtype: dict
        </comment-en>
        """
        retval = {}

        try:
            pool_obj = self.search_kvn_storage_pools(pool)[0]
            if not pool_obj:
                raise KaresansuiVirtException(_("No storage pool '%s' could be found.") % pool)

            pool_type = pool_obj.get_info()['type']
            if pool_type == "dir":
                vols = pool_obj.vol_listVolumes()
                for vol in vols:
                    vol_obj = pool_obj.vol_storageVolLookupByName(vol)
                    try:
                        exec("value = vol_obj.%s()" % attr)
                        retval[vol] = value
                    except:
                        pass
            else:
                value = pool_obj.get_info()['target']['path']
                retval[pool] = value
        except:
            pass

        return retval

    def get_storage_volume_iscsi_rpath_bystorage(self, pool, volume):
        """<comment-ja>
        ストレージプール名とストレージボリューム名から、ストレージのREAL PATHを取得します。
        </comment-ja>
        <comment-en>
        TODO: To include comments in English
        </comment-en>
        """
        ret = None
        try:
            pool_obj = self.search_kvn_storage_pools(pool)[0]
            if not pool_obj:
                raise KaresansuiVirtException(_("No storage pool '%s' could be found.") % pool)

            vol_obj = pool_obj.vol_storageVolLookupByName(volume)
            ret = vol_obj.key()
        except:
            pass

        return ret

    def get_storage_volume_bydomain(self, domain, image_type=None, attr="name"):
        """<comment-ja>
        ドメインの名前からボリュームの一覧を取得する
        @param domain: ドメイン名
        @param image_type: イメージの種別
                     "os"    :ゲストOS本体のイメージファイル
                     "disk"  :拡張ディスクのイメージファイル
                     未指定  :ドメインに属する全てのイメージファイル
        @param attr: 取得する属性
                     "name"  :ボリュームの名前(UUID形式)
                     "key"   :ボリュームのキー
                     "path"  :ボリュームのパス
                     "info"  :ボリュームの情報
                     未指定  :nameが指定されたものとする

                     attr 'info' depends on virStorageVolInfo structure.
                       int type;                      virStorageVolType flags
                                                      0 :Regular file
                                                      1 :Block
                       unsigned long long capacity;   Logical size bytes
                       unsigned long long allocation; Current allocation bytes
        @return: ストレージボリューム名と対応するデータの辞書配列
        @rtype: dict
        </comment-ja>
        <comment-en>
        Get name of storage volume in the specified domain.

        @param domain: domain name
        @param image_type: type of image file
                     "os"    :os image only
                     "disk"  :extended disk image only
                     none    :all images that domain uses
        @param attr: volume attribute that you want to get
                     "name"  :name of volume (UUID style)
                     "key"   :key of volume
                     "path"  :path of volume
                     "info"  :volume information
                     none    :same as 'name' is specified

        @return: dict of storage volume
        @rtype: dict
        </comment-en>
        """
        retval = {}

        regex = []
        if image_type == "os":
            regex.append("%s/images/%s\.img$" % (domain,domain,))
        if image_type == "disk":
            regex.append("%s/disk/[0-9\.]+\.img$" % (domain,))
        regex_str = "|".join(regex)

        try:
            guest_obj = self.search_kvg_guests(domain)[0]
            if not guest_obj:
                raise KaresansuiVirtException(_("Domain could not be found. name=%s") % \
                                          domain)

            os_root = guest_obj.get_info()['os_root']

            for info in guest_obj.get_disk_info():
                try:
                    target = info['target']['dev']
                except:
                    target = None

                try:
                    source = info['source']['file']
                except:
                    try:
                        source = info['source']['dev']
                    except:
                        source = None

                pools = []
                if image_type == "os":
                   if os_root is not None and target == os.path.basename(os_root):
                       pools = self.get_storage_pool_name_byimage(source)
                elif image_type == "disk":
                   if os_root is not None and target != os.path.basename(os_root):
                       pools = self.get_storage_pool_name_byimage(source)
                else:
                    pools = self.get_storage_pool_name_byimage(source)

                if len(pools) > 0:
                    for _pool in pools:
                        vols = self.get_storage_volume_bypool(_pool, attr=attr)
                        for vol,value in vols.items():
                            path = self.get_storage_volume_iscsi_rpath_bystorage(_pool,vol)
                            if path[0:5] != "/dev/":
                                path = os.path.realpath(path)
                            if source == path and not vol in list(retval.keys()):
                                retval[vol] = value

        except:
            pass

        return retval


    def get_storage_volume_symlink(self, path):
        """<comment-ja>
        ディスクイメージのパスからストレージボリューム(symlink)の名前を取得します。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        ret = []

        paths = [path]
        realpath = os.path.realpath(path)

        # Includes realpath as detecting target if it is symbolic link.
        if realpath != path:
            paths.append(realpath)

        try:
            pool_objs = self.search_kvn_storage_pools()
            if not pool_objs:
                raise KaresansuiVirtException(_("No storage pools could be found."))

            for pool_obj in pool_objs:
                pool_info = pool_obj.get_info()
                if pool_info['type'] != 'dir' or pool_info['is_active'] is False:
                    continue

                vols = pool_obj.vol_listVolumes()
                for vol in vols:
                    vol_path = "%s/%s" % (pool_info['target']['path'], vol)
                    vol_real_path = os.path.realpath(vol_path)
                    if path == vol_real_path:
                        #ret.append(vol_real_path)
                        ret.append(vol)
        except:
            pass
        return ret

    def get_storage_volume_iscsi_bysymlink(self, symlink):
        """<comment-ja>
        example形式のiscsiパスからlibvirtのストレージボリューム情報を取得します。
        
        @param symlink: example) 'ip-192.168.100.100:3260-iscsi-iqn.2010-01.info.karesansui-project:iscsi-123-lun-1'
        @return: {pool: プール名,volume: ボリューム名,rpath:iscsiのby-path}
        </comment-ja>
        <comment-en>
        TODO: To include comments in English
        </comment-en>
        """
        pools = self.search_kvn_storage_pools()
        rpath = "%s/%s" % (ISCSI_DEVICE_DIR, symlink)
        ret = None
        for pool in pools:
            name = pool.get_storage_name()
            if self.get_storage_pool_type(name) == 'iscsi':
                volumes = self.get_storage_volume_bypool(name, 'key')
                for vkey in list(volumes.keys()):
                    if rpath == volumes[vkey]:
                        ret = {"pool" : name,
                               "volume" : vkey,
                               "rpath" : volumes[vkey],
                               }
                        break
        return ret

    def get_storage_volume_iscsi_block_bypool(self, pool):
        """<comment-ja>
        ストレージプールの名前からiSCSIブロックデバイスのボリュームの一覧を取得する
        @param pool: プール名
        @return: ストレージボリューム名の配列
        @rtype: dict
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        retval = []

        try:
            active_pool = self.list_active_storage_pool()
            #inactive_pool = self.list_inactive_storage_pool()
            inactive_pool = []
            pools = inactive_pool + active_pool

            pool_obj = self.search_kvn_storage_pools(pool)[0]
            if not pool_obj:
                raise KaresansuiVirtException(_("No storage pool '%s' could be found.") % pool)

            vols = pool_obj.vol_listVolumes()
            for vol in vols:
                vol_obj = pool_obj.vol_storageVolLookupByName(vol)
                vol_key = vol_obj.key()
                vol_key = vol_key.replace("%s/" % (ISCSI_DEVICE_DIR), "")
                regex = re.compile(r"^%s" % (re.escape(vol_key)))
                is_mount = False
                for pool in pools:
                    if regex.match(pool):
                        is_mount = True

                if is_mount is False:
                    retval.append(vol)
        except:
            pass

        return retval


class KaresansuiVirtGuest:

    def __init__(self, conn, name=None):
        self.connection = conn
        self._conn = self.connection._conn
        self.set_domain_name(name)

    def get_json(self):
        """<comment-ja>
        JSON形式でKaresansuiVirtGuest情報を返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        
        ret = {}
        ret['name'] = self.get_domain_name()
        ret.update(self.get_info())
        return ret

    def set_domain_name(self,name=None):
        if is_uuid(name):
            self.domain = conn.uuid_to_domname(name)
        else:
            self.domain = name

    def get_domain_name(self):
        return self.domain

    def get_info(self):
        dom = self._conn.lookupByName(self.get_domain_name())
        data = dom.info()
        try:
            os_type = dom.OSType()
        except:
            os_type = None
        try:
            uuid = dom.UUIDString()
        except:
            uuid = None

        try:
            param = ConfigParam(dom.name())
            xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
            if not os.path.exists(xml_file):
                if dom._conn.getURI() in list(available_virt_uris().values()):
                    ConfigFile(xml_file).write(dom.XMLDesc(0))
                    if os.getuid() == 0 and os.path.exists(xml_file):
                        r_chgrp(xml_file,KARESANSUI_GROUP)
            #param.load_xml_config(xml_file)
            param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

            vm_type = param.domain_type
            os_root = param.os_root

        except:
            vm_type = uri_split(self._conn.getURI())["scheme"]
            os_root = "unknown"
            pass

        try:
            self.connection.hypervisor
        except:
            self.connection.hypervisor = self.connection.get_hypervisor_type()
        hypervisor = self.connection.hypervisor

        try:
            self.connection.hvVersion
        except:
            try:
                self.connection.hvVersion = libvirtmod.virConnectGetVersion(self._conn._o)
            except:
                pass
        try:
            hvVersion = self.connection.hvVersion
            hvVersion_major = hvVersion / 1000000
            hvVersion %= 1000000
            hvVersion_minor = hvVersion / 1000
            hvVersion_rel = hvVersion % 1000
            hv_version = "%s %d.%d.%d" %(hypervisor, hvVersion_major, hvVersion_minor, hvVersion_rel)
        except:
            hv_version = None

        return {
                "state"     : data[0],
                "maxMem"    : data[1],
                "memory"    : data[2],
                "nrVirtCpu" : data[3],
                "cpuTime"   : data[4],
                "OSType"    : os_type,
                "VMType"    : vm_type,
                "hypervisor": hypervisor,
                "hv_version": hv_version,
                "os_root"   : os_root,
                "uuid"      : uuid,
        }

    def get_netinfo(self):
        info = {}
        dom = self._conn.lookupByName(self.get_domain_name())
        dom_id = dom.ID()
        if self.get_info()["VMType"] == "kvm":
            #eth_info = get_ifconfig_info("regex:^eth")
            eth_info = get_ifconfig_info("regex:^br")
            for dev,value in eth_info.items():
                info[dev] = value
        else:
            vif_info = get_ifconfig_info("regex:^vif%d\.[0-9]" % dom_id)
            for dev,value in vif_info.items():
                dev = dev.replace("vif%d." % (dom_id,), "eth")
                info[dev] = value
        return info

    def get_disk_info(self):
        infos = []
        dom = self._conn.lookupByName(self.get_domain_name())

        param = ConfigParam(dom.name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        for info in param.disks:
            driver = {}
            source = {}
            target = {}
            type   = info['disk_type']
            device = info['device']

            try:
                driver['name'] = info["driver_name"]
            except:
                driver['name'] = None
            try:
                driver['type'] = info["driver_type"]
            except:
                driver['type'] = None

            if type == 'block':
                source['dev'] = info['path']
                source_path = source['dev']
            else:
                source['file'] = info['path']
                source_path = source['file']

            target['dev'] = info['target']
            target['bus'] = info['bus']

            if os.path.exists(source_path):
                img_info = get_disk_img_info(source_path)
                try:
                    img_size = img_info['virtual_size']
                except:
                    img_size = img_info['real_size']
                source['size'] = get_filesize_MB(img_size)
            else:
                source['size'] = 0
            info = {
                   "type":type,
                   "device":device,
                   "driver":driver,
                   "source":source,
                   "target":target,
                   }
            infos.append(info)
        return infos

    def get_vcpus_info(self):
        dom = self._conn.lookupByName(self.get_domain_name())

        param = ConfigParam(dom.name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(1))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        try:
            max_vcpus = int(param.max_vcpus)
        except:
            max_vcpus = None
        try:
            if self.status() != VIR_DOMAIN_SHUTOFF:
                vcpus = self.get_info()['nrVirtCpu']
            else:
                vcpus = None
        except:
            vcpus = None
        try:
            bootup_vcpus = int(param.vcpus)
        except:
            bootup_vcpus = None

        return {
                "max_vcpus"    :max_vcpus,
                "vcpus"        :vcpus,
                "bootup_vcpus" :bootup_vcpus,
               }

    def get_interface_info(self):
        infos = []
        dom = self._conn.lookupByName(self.get_domain_name())

        param = ConfigParam(dom.name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(0))

        for info in param.interfaces:
            mac = {}
            source = {}
            script = {}
            target = {}
            type           = info['type']
            mac['address'] = info['mac']
            script['path'] = info['script']
            target['dev']  = info['target']
            if str(type) == "network":
                try:
                    source['network'] = info['network']
                except:
                    source['network'] = None
            else:
                try:
                    source['bridge']  = info['bridge']
                except:
                    source['bridge']  = None

            if_info = {
                   "type":type,
                   "mac":mac,
                   "source":source,
                   "script":script,
                   "target":target,
                   }
            infos.append(if_info)

        return infos

    def get_graphics_info(self):
        dom = self._conn.lookupByName(self.get_domain_name())

        """ current info """
        param = ConfigParam(dom.name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(0))

        type     = param.get_graphics_type()
        port     = param.get_graphics_port()
        autoport = param.get_graphics_autoport()
        listen   = param.get_graphics_listen()
        keymap   = param.get_graphics_keymap()
        current_info = {
                       "type"    :type,
                       "port"    :port,
                       "autoport":autoport,
                       "listen"  :listen,
                       "keymap"  :keymap,
                       }

        """ current setting """
        param = ConfigParam(self.get_domain_name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        type     = param.get_graphics_type()
        port     = param.get_graphics_port()
        autoport = param.get_graphics_autoport()
        listen   = param.get_graphics_listen()
        keymap   = param.get_graphics_keymap()
        passwd   = param.get_graphics_passwd()
        current_setting = {
                       "type"    :type,
                       "port"    :port,
                       "autoport":autoport,
                       "listen"  :listen,
                       "keymap"  :keymap,
                       "passwd"  :passwd,
                       }

        return {"info":current_info,"setting":current_setting}

    def create(self):
        if self.is_creatable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())
            dom.create()
            for x in range(0,5):
                time.sleep(1)
                if self.status() != VIR_DOMAIN_SHUTOFF:
                    break

    def shutdown(self):
        if self.is_shutdownable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())
            dom.shutdown()
            for x in range(0,120):
                time.sleep(1)
                if self.status() == VIR_DOMAIN_SHUTOFF:
                    break

    def reboot(self):
        if self.is_shutdownable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())

            """
            dom.reboot(0)
            """
            dom.shutdown()
            for x in range(0,480):
                time.sleep(1)
                if self.status() == VIR_DOMAIN_SHUTOFF:
                    break
            dom.create()

            for x in range(0,30):
                time.sleep(1)
                if self.status() != VIR_DOMAIN_SHUTOFF:
                    break

    def destroy(self):
        if self.is_destroyable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())
            dom.destroy()
            for x in range(0,120):
                time.sleep(1)
                if self.status() == VIR_DOMAIN_SHUTOFF:
                    break

    def suspend(self):
        if self.is_suspendable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())
            dom.suspend()
            for x in range(0,5):
                time.sleep(1)
                if self.status() == VIR_DOMAIN_PAUSED:
                    break

    def resume(self):
        if self.is_resumable() is True:
            time.sleep(1)
            dom = self._conn.lookupByName(self.get_domain_name())
            dom.resume()
            for x in range(0,5):
                time.sleep(1)
                if self.status() != VIR_DOMAIN_PAUSED:
                    break

    def undefine(self):
        dom = self._conn.lookupByName(self.get_domain_name())
        dom.undefine()

    def status(self):
        return self.get_info()["state"]

    def save(self,file):
        dom = self._conn.lookupByName(self.get_domain_name())
        dom.save(file)
        for x in range(0,120):
            time.sleep(1)
            if self.status() == VIR_DOMAIN_SHUTOFF:
                break


    def set_current_snapshot(self,id=None):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        param.set_current_snapshot(id)

        xml_generator = XMLConfigGenerator()
        cfgxml = xml_generator.generate(param)
        self._conn.defineXML(cfgxml)

        sync_config_generator(param, self.get_domain_name())


    def autostart(self, flag=None):
        dom = self._conn.lookupByName(self.get_domain_name())

        if dom._conn.getURI() in list(available_virt_uris().values()):
            if self.connection.get_hypervisor_type() == "Xen":
                autostart_file = "%s/%s" %(VIRT_XENDOMAINS_AUTO_DIR,self.get_domain_name())

                if flag == True:
                    if not os.path.exists(autostart_file):
                        command_args = [
                        "/bin/ln", "-s",
                        "%s/%s" %(self.connection.config_dir,self.get_domain_name()),
                        "%s" % VIRT_XENDOMAINS_AUTO_DIR
                        ]
                        ret = ExecCmd(command_args)
                    return True
                elif flag == False:
                    if os.path.exists(autostart_file):
                        os.unlink(autostart_file)
                    return True
                else:
                    return os.path.lexists(autostart_file)

            elif self.connection.get_hypervisor_type() == "QEMU":
                autostart_file = "%s/%s.xml" %(VIRT_AUTOSTART_CONFIG_DIR,self.get_domain_name())
                if flag == True:
                    return dom.setAutostart(flag)
                elif flag == False:
                    return dom.setAutostart(flag)
                else:
                    return os.path.exists(autostart_file)

        else:
            if flag == True:
                return dom.setAutostart(flag)
            elif flag == False:
                return dom.setAutostart(flag)

        return False

    def next_disk_target(self,bus=None):
        dom = self._conn.lookupByName(self.get_domain_name())
        serials = []

        param = ConfigParam(dom.name())
        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, dom.name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if bus is None:
            bus = self.connection.bus_types[0]

        if bus == "virtio":
            prefix_regex = "vd"
        elif bus == "scsi":
            prefix_regex = "sd"
        else:
            prefix_regex = "hd|xvd"

        prefix = None
        for info in param.disks:
            block_name = info['target']
            p = re.compile(r"""^(?P<prefix>%s)(?P<serial>[a-z])$""" % prefix_regex)
            m = p.match(block_name)
            if m is not None:
                prefix = m.group("prefix")
                serials.append(m.group("serial"))

        if prefix is None:
            prefix = prefix_regex

        for i,_x in enumerate('abcdefghijklmnopqrstuvwxyz'):
          if not _x in serials:
            next_serial = _x
            break

        return "%s%s" %(prefix, next_serial)

    """This is unused method
    def add_disk(self, path, target, size, is_sparse=True, bus=None,
                 driver_name=None, driver_type=None):
        name = self.get_domain_name()

        # TODO VIRT_DOMAINS_DIR
        domain_disk_dir = "%s/%s/disk" % (VIRT_DOMAINS_DIR,name,)
        if not os.path.exists(domain_disk_dir):
            os.makedirs(domain_disk_dir)

        if bus is None:
            bus = self.connection.bus_types[0]

        if driver_type is None:
            if driver_name == "qemu":
                driver_type = "qcow2"
            else:
                driver_type = "raw"

        try:
            MakeDiskImage(path,int(size),driver_type, is_sparse)
            return self.append_disk(path, target, bus,
                                    driver_name=driver_name, driver_type=driver_type)
        except:
            if os.path.exists(path) is True:
                os.remove(path)
            raise
    """

    def append_disk(self, path, target, bus=None, disk_type=None, driver_name=None, driver_type=None, disk_device='disk'):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if bus is None:
            bus = self.connection.bus_types[0]

        if disk_type != 'block':
            if driver_name is None:
                if self.connection.get_hypervisor_type() == "QEMU":
                    driver_name = "qemu"
            if driver_type is None:
                if driver_name == "qemu":
                    driver_type = "qcow2"

        param.add_disk(path,
                       target,
                       disk_device,
                       bus,
                       disk_type=disk_type,
                       driver_name=driver_name,
                       driver_type=driver_type)

        try:
            from karesansui.lib.virt.config import XMLDiskConfigGenerator
            generator = XMLDiskConfigGenerator()
            generator.set_path(path)
            generator.set_target(target)
            cfg = generator.generate(None)

            # qemu: cannot attach device on inactive domain
            if self.connection.get_hypervisor_type() == "QEMU" and dom.isActive() == 0:
                True
            # qemu: disk bus 'ide' cannot be hotplugged.
            elif self.connection.get_hypervisor_type() == "QEMU" and bus is not None and bus == "ide":
                True
            """Do not attach device whatever domain is active or not.
            else:
                dom.attachDevice(cfg)
            """

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)
        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def delete_disk(self, target):
        status = self.status()
        if status == VIR_DOMAIN_PAUSED:
            self.resume()
            time.sleep(2)
            #raise KaresansuiVirtException("Domain %s is suspended." % self.get_domain_name())

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        path = param.get_disk_path(target)

        # physical disk remove
        if path is not None and os.path.exists(path) is True:
            try:
                os.remove(path)
            except:
                self.logger.info("You do not have a disk file. - %s" % path)
                raise
        param.delete_disk(target)

        try:
            from karesansui.lib.virt.config import XMLDiskConfigGenerator
            generator = XMLDiskConfigGenerator()
            generator.set_target(target)
            generator.set_path(path)
            cfg = generator.generate(None)

            """Do not detach device whatever domain is active or not.
            try:
                dom.detachDevice(cfg)
            except:
                xml_generator = XMLConfigGenerator()
                cfgxml = xml_generator.generate(param)
                self._conn.defineXML(cfgxml)
            """
            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)

            if status == VIR_DOMAIN_PAUSED:
                self.suspend()
        except KaresansuiConfigParamException as e:
            raise e
        except Exception as e:
            raise e

        sync_config_generator(param, self.get_domain_name())

    def append_interface(self,mac,bridge=None,network=None,model=None):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if network is not None:
            netinfo = self.connection.search_kvn_networks(network)[0].get_info()
            bridge = netinfo['bridge']['name']

        if bridge[0:5] == 'xenbr':
            script = "vif-bridge"
            model  = None
        else:
            script = None
            model  = "virtio"
        mac = mac.lower()
        param.add_interface(mac,"bridge",bridge,script,model=model)

        try:
            from karesansui.lib.virt.config import XMLInterfaceConfigGenerator
            generator = XMLInterfaceConfigGenerator()
            generator.set_mac(mac)
            generator.set_bridge(bridge)
            if script is not None:
                generator.set_script(script)
            cfg = generator.generate(None)

            # qemu: cannot attach device on inactive domain
            if self.connection.get_hypervisor_type() == "QEMU" and dom.isActive() == 0:
                True
            else:
                dom.attachDevice(cfg)

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)

        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def delete_interface(self,mac,force=False):

        status = self.status()
        if status == VIR_DOMAIN_PAUSED:
            self.resume()
            time.sleep(2)
            #raise KaresansuiVirtException("Domain %s is suspended." % self.get_domain_name())

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        current_snapshot = param.get_current_snapshot()
        if force is True:
            param.load_xml_config(dom.XMLDesc(0))
            if current_snapshot is not None:
                param.set_current_snapshot(current_snapshot)

        bridge = None
        for info in param.interfaces:
            if info["mac"] == mac:
                bridge = info['bridge']

        bridge = None
        if bridge is None:
            param.load_xml_config(dom.XMLDesc(0))
            for info in param.interfaces:
                if info["mac"] == mac:
                    bridge = info['bridge']

        mac = mac.lower()
        param.delete_interface(mac)

        try:
            from karesansui.lib.virt.config import XMLInterfaceConfigGenerator
            generator = XMLInterfaceConfigGenerator()
            generator.set_mac(mac)
            if bridge is not None:
                generator.set_bridge(bridge)
            cfg = generator.generate(None)

            if self.connection.get_hypervisor_type() == "Xen":
                try:
                    dom.detachDevice(cfg)
                except:
                    pass

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)

            if status == VIR_DOMAIN_PAUSED:
                self.suspend()
        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def modify_mac_address(self,old,new):

        status = self.status()
        if status == VIR_DOMAIN_PAUSED:
            self.resume()
            time.sleep(2)
            #raise KaresansuiVirtException("Domain %s is suspended." % self.get_domain_name())

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        new_interfaces = []

        old = old.lower()
        new = new.lower()
        for info in param.interfaces:
            if info["mac"] == old:
                bridge = info['bridge']
                info["mac"] = new
            new_interfaces.append(info)
        param.interfaces = new_interfaces

        try:
            """
            try:
                self.delete_interface(old,True)
                self.append_interface(new,bridge)
            except:
                xml_generator = XMLConfigGenerator()
                cfgxml = xml_generator.generate(param)
                self._conn.defineXML(cfgxml)
            """
            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)

            if status == VIR_DOMAIN_PAUSED:
                self.suspend()
        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def set_memory(self,maxmem=None,memory=None):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if maxmem:
            param.set_max_memory(maxmem)
        if memory:
            param.set_memory(memory)

        try:
            dom.setMaxMemory(param.get_max_memory("k"))
            dom.setMemory(param.get_memory("k"))

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)
        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def set_vcpus(self,max_vcpus=None,vcpus=None):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if max_vcpus is not None:
            param.set_max_vcpus(int(max_vcpus))

        if vcpus is not None:
            param.set_vcpus(int(vcpus))

        param.set_max_vcpus_limit(int(self.connection.get_max_vcpus()))
        param.set_vcpus_limit(int(self.get_vcpus_info()['max_vcpus']))

        try:
            # qemu: cannot change vcpu count of an active domain
            if self.connection.get_hypervisor_type() == "QEMU" and dom.isActive() == 1:
                True
            else:
                dom.setVcpus(param.get_vcpus())

            xml_generator = XMLConfigGenerator()
            cfgxml = xml_generator.generate(param)
            self._conn.defineXML(cfgxml)
        except:
            raise

        sync_config_generator(param, self.get_domain_name())

    def set_graphics(self,port=None,listen=None,passwd=None,keymap=None,type='vnc'):

        from karesansui.lib.virt.config import ConfigParam
        param = ConfigParam(self.get_domain_name())
        dom = self._conn.lookupByName(self.get_domain_name())

        xml_file = "%s/%s.xml" % (VIRT_XML_CONFIG_DIR, self.get_domain_name())
        if not os.path.exists(xml_file):
            if dom._conn.getURI() in list(available_virt_uris().values()):
                ConfigFile(xml_file).write(dom.XMLDesc(0))
                if os.getuid() == 0 and os.path.exists(xml_file):
                    r_chgrp(xml_file,KARESANSUI_GROUP)
        #param.load_xml_config(xml_file)
        param.load_xml_config(dom.XMLDesc(VIR_DOMAIN_XML_INACTIVE))

        if port is not None:
            param.set_graphics_port(port)

        if listen is not None:
            param.set_graphics_listen(listen)

        if passwd is not None:
            param.set_graphics_passwd(passwd)

        if keymap is not None:
            param.set_graphics_keymap(keymap)

        if type is not None:
            param.set_graphics_type(type)

        xml_generator = XMLConfigGenerator()
        cfgxml = xml_generator.generate(param)
        self._conn.defineXML(cfgxml)

        sync_config_generator(param, self.get_domain_name())

    def is_creatable(self):
        """<comment-ja>
        ゲストOS(ドメイン)を起動することができるか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.status() == VIR_DOMAIN_SHUTOFF:
            return True
        else:
            return False

    def is_shutdownable(self):
        """<comment-ja>
        ゲストOS(ドメイン)をシャットダウンすることができるか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        
        status = self.status()
        if status == VIR_DOMAIN_RUNNING \
               or status == VIR_DOMAIN_BLOCKED \
               or status == VIR_DOMAIN_PAUSED:
            return True
        else:
            return False

    def is_destroyable(self):
        """<comment-ja>
        ゲストOS(ドメイン)を強制停止することができるか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        status = self.status()
        if status == VIR_DOMAIN_RUNNING \
               or status == VIR_DOMAIN_BLOCKED \
               or status == VIR_DOMAIN_PAUSED:
            return True
        else:
            return False

    def is_suspendable(self):
        """<comment-ja>
        ゲストOS(ドメイン)の一時停止することができるか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        status = self.status()
        if status == VIR_DOMAIN_NOSTATE \
               or status ==VIR_DOMAIN_RUNNING \
               or status == VIR_DOMAIN_BLOCKED:
            return True
        else:
            return False

    def is_resumable(self):
        """<comment-ja>
        ゲストOS(ドメイン)再開することができるか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.status() == VIR_DOMAIN_PAUSED:
            return True
        else:
            return False

    def is_active(self):
        """<comment-ja>
        ゲストOSの状態がactiveか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return (self.get_domain_name() in self.connection.list_active_guest())

    def is_inactive(self):
        """<comment-ja>
        ゲストOSの状態がinactiveか。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return (self.get_domain_name() in self.connection.list_inactive_guest())

    def is_takable_snapshot(self):
        """<comment-ja>
        スナップショットを作成できる状態か。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.status() == VIR_DOMAIN_SHUTOFF:
            return False
        else:
            return True

    
class KaresansuiVirtNetwork:

    def __init__(self, conn, name=None):
        self.connection = conn
        self._conn = self.connection._conn
        self.set_network_name(name)

    def set_network_name(self,name=None):
        self.network_name = name
    def get_network_name(self):
        return self.network_name

    def load(self):
        param = NetworkConfigParam(self.get_network_name())
        param.load_xml_config("%s/%s.xml" % (VIRT_NETWORK_CONFIG_DIR, self.get_network_name()))

    def start(self):
        net = self._conn.networkLookupByName(self.get_network_name())
        try:
            net.create()
        except libvirt.libvirtError as e:
            raise KaresansuiVirtException(_("Could not start network '%s' (%s)") % (self.network_name, e))

    def stop(self):
        net = self._conn.networkLookupByName(self.get_network_name())
        try:
            # now isActive() is deplicated.
            # if net.isActive() != 0:
            if net.name() in self._conn.listNetworks():
                net.destroy()
        except libvirt.libvirtError as e:
            raise KaresansuiVirtException(_("Could not stop network '%s' (%s)") % (self.network_name, e))

    def undefine(self):
        net = self._conn.networkLookupByName(self.get_network_name())
        net.undefine()

    def autostart(self, flag=None):
        net = self._conn.networkLookupByName(self.get_network_name())
        current_flag = net.autostart()
        if flag is None:
            return current_flag
        else:
            if current_flag != flag:
                return net.setAutostart(flag)
            else:
                return True

    def get_json(self):
        """<comment-ja>
        JSON形式でKaresansuiVirtNetwork情報を返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        
        ret = {}
        ret['name'] = self.get_network_name()
        ret.update(self.get_info())
        return ret

    def get_info(self):
        try:
            net = self._conn.networkLookupByName(self.get_network_name())
            autostart = net.autostart()
        except Exception as e:
            raise KaresansuiVirtException("Could not get network: %s"
                                            % str(e))

        param = NetworkConfigParam(self.get_network_name())
        xml_file = "%s/%s.xml" % (VIRT_NETWORK_CONFIG_DIR, self.get_network_name())
        if not os.path.exists(xml_file):
            ConfigFile(xml_file).write(net.XMLDesc(0))
            if os.getuid() == 0 and os.path.exists(xml_file):
                r_chgrp(xml_file,KARESANSUI_GROUP)
        param.load_xml_config(xml_file)


        name        = param.get_network_name()
        uuid        = param.get_uuid()
        bridge_name = param.get_bridge()
        bridge_stp  = param.get_bridge_stp()
        bridge_forwardDelay = param.get_bridge_forwardDelay()
        bridge = {
                   "name"        :bridge_name,
                   "stp"         :bridge_stp,
                   "forwardDelay":bridge_forwardDelay,
                 }

        dhcp_start = param.get_dhcp_start()
        dhcp_end   = param.get_dhcp_end()
        dhcp = {
                   "start":dhcp_start,
                   "end"  :dhcp_end,
               }

        ip_address = param.get_ipaddr()
        ip_netmask = param.get_netmask()
        ip = {
                   "address":ip_address,
                   "netmask":ip_netmask,
                   "dhcp"   :dhcp,
             }

        forward_dev  = param.get_forward_dev()
        forward_mode = param.get_forward_mode()
        forward = {
                   "mode":forward_mode,
                   "dev" :forward_dev,
             }

        is_active = self.is_active()

        return {
                "name"     :name,
                "uuid"     :uuid,
                "bridge"   :bridge,
                "dhcp"     :dhcp,
                "ip"       :ip,
                "forward"  :forward,
                "autostart":autostart,
                "is_active":is_active,
        }

    def get_network_config_param(self):
        return NetworkConfigParam(self.get_info())

    def is_active(self):
        return (self.network_name in self._conn.listNetworks())

    def is_inactive(self):
        return (self.network_name in self._conn.listDefinedNetworks())

class KaresansuiVirtStorage:

    def __init__(self, conn, name=None):
        self.connection = conn
        self._conn = self.connection._conn
        self.set_storage_name(name)

    def set_storage_name(self,name=None):
        self.storage_name = name

    def get_storage_name(self):
        return self.storage_name

class KaresansuiVirtStoragePool(KaresansuiVirtStorage):

    def build(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            return pool.build(libvirt.VIR_STORAGE_POOL_BUILD_NEW)
        except Exception as e:
            raise KaresansuiVirtException("Could not build storage pool: %s"
                                            % str(e))

    def create(self, name=None, flags=0):
        if name is not None:
            self.set_storage_name(name)
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            ret = pool.create(flags)
            pool.refresh(0)
            return ret
        except Exception as e:
            raise KaresansuiVirtException("Could not create storage pool: %s"
                                            % str(e))

    def start(self, cfgxml, flags, name=None):
        if name:
            self.set_storage_name(name)
            
        # define
        try:
            ret = self._conn.storagePoolDefineXML(cfgxml, flags) # virStoragePoolDefineXML
            #ret = libvirtmod.virStoragePoolCreateXML(self._conn._o,cfgxml, 0)
        except libvirt.libvirtError as e:
            raise KaresansuiVirtException("Could not start pool '%s' (%s)" \
                                          % (self.get_storage_name, e))
        ret1 = self.build()
        ret2 = self.create()
        return ret2

    def load(self):
        param = StoragePoolConfigParam(self.get_storage_name())
        param.load_xml_config("%s/%s.xml" \
                              % (VIRT_STORAGE_CONFIG_DIR, self.get_storage_name()))


    def destroy(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            return pool.destroy()
        except Exception as e:
            raise KaresansuiVirtException("Could not destroy storage pool: %s" \
                                            % str(e))

    def delete(self, flags):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            return pool.delete(flags)
        except Exception as e:
            raise KaresansuiVirtException("Could not delete storage pool: %s" \
                                            % str(e))

    def autostart(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        return pool.autostart()

    def is_autostart(self):
        ret = self.autostart()
        if ret == 0:
            return False # OFF
        elif ret == 1:
            return True # ON
        else:
            return None # ERR

    def set_autostart(self, flag=None):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        return pool.setAutostart(flag)

    def get_json(self):
        """<comment-ja>
        JSON形式でKaresansuiVirtNetwork情報を返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        ret = {}
        ret['name'] = self.get_storage_name()
        ret.update(self.get_info())
        return ret

    def get_info(self):
        try:
            pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        except Exception as e:
            raise KaresansuiVirtException("Could not get the storage pool: %s" \
                                            % str(e))

        param = StoragePoolConfigParam(self.get_storage_name())
        param.load_xml_config(pool.XMLDesc(0))
        return {"name" : param.get_storage_name(),
                "uuid" : param.get_uuid(),
                "type" : param.get_pool_type(),
                "allocation" : param.get_allocation(),
                "capacity" : param.get_capacity(),
                "available" : param.get_available(),
                "source" : {"dev_path" : param.get_source_dev_path(),
                            "dir_path" : param.get_source_dir_path(),
                            "h_name" : param.get_source_h_name(),
                            "f_type" : param.get_source_f_type(),
                            },
                "target" : {"path" : param.get_target_path(),
                            "p_owner" : param.get_target_permissions_owner(),
                            "p_group" : param.get_target_permissions_group(),
                            "p_mode" : param.get_target_permissions_mode(),
                            "p_label" : param.get_target_permissions_label(),
                            "e_format" : param.get_target_e_format(),
                            "e_s_type" : param.get_target_encryption_s_type(),
                            "e_s_uuid" : param.get_target_encryption_s_uuid(),
                            },
                "is_active"    : self.is_active(),
                "is_autostart" : self.is_autostart(),
            }

    def is_active(self):
        return (self.storage_name in self._conn.listStoragePools())

    def is_inactive(self):
        return (self.storage_name in self._conn.listdefinedStoragePools())

    def vol_createXML(self, xmldesc, flags):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            return pool.createXML(xmldesc, flags)
        except Exception as e:
            raise KaresansuiVirtException("Could not create storage volume: %s" % str(e))

    def vol_numOfVolumes(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        return pool.numOfVolumes()
        
    def vol_storageVolLookupByName(self, name):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        return pool.storageVolLookupByName(name)
        
    def vol_listVolumes(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        return pool.listVolumes()

    def search_kvn_storage_volumes(self, conn):
        vols_obj = []
        for vol in self.vol_listVolumes():
            vol_obj = KaresansuiVirtStorageVolume(conn)
            vol_obj.set_storage_name(self.get_storage_name())
            vol_obj.set_storage_volume_name(vol)
            
            vols_obj.append(vol_obj)
        return vols_obj

class KaresansuiVirtStorageVolume(KaresansuiVirtStorage):

    storage_volume_name = None

    def set_storage_volume_name(self,name=None):
        self.storage_volume_name = name

    def get_storage_volume_name(self):
        return self.storage_volume_name

    def load(self):
        param = StorageVolumeConfigParam(self.get_storage_volume_name())
        param.load_xml_config("%s/%s.xml" \
                              % (VIRT_STORAGE_CONFIG_DIR, self.get_storage_volume_name()))

    def delete(self, flags):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            vol = pool.storageVolLookupByName(self.get_storage_volume_name())
            return vol.delete(flags)
        except Exception as e:
            raise KaresansuiVirtException("Could not delete storage volume: %s"
                                            % str(e))

    def get_json(self):
        """<comment-ja>
        JSON形式でKaresansuiVirtNetwork情報を返却する。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        pass
        #ret = {}
        #ret['name'] = self.get_network_name()
        #ret.update(self.get_info())
        #return ret

    def get_info(self):
        pool = self._conn.storagePoolLookupByName(self.get_storage_name())
        try:
            vol = pool.storageVolLookupByName(self.get_storage_volume_name())
        except Exception as e:
            raise KaresansuiVirtException("Could not get the storage volume: %s"
                                            % str(e))

        param = StorageVolumeConfigParam(self.get_storage_name())
        try:
            param.load_xml_config(vol.XMLDesc(0))
        except libvirt.libvirtError as le:
            # TODO test!!
            self.connection.refresh_pools()
            param.load_xml_config(vol.XMLDesc(0))

        real = param.get_symlink2real()
        return {"name" : param.get_storage_name(),
                "uuid" : param.get_uuid(),
                "key" : param.get_key(),
                "allocation" : param.get_allocation(),
                "capacity" : param.get_capacity(),
                "c_unit" : param.get_c_unit(),
                "source" : param.get_source(),
                "target" : {"path" : param.get_target_path(),
                            "f_type" : param.get_target_f_type(),
                            "p_owner" : param.get_target_permissions_owner(),
                            "p_group" : param.get_target_permissions_group(),
                            "p_mode" : param.get_target_permissions_mode(),
                            "p_label" : param.get_target_permissions_label(),
                            "b_path" : param.get_backingStore_path(),
                            "b_format" : param.get_backingStore_format(),
                            "b_p_owner" : param.get_backingStore_permissions_owner(),
                            "b_p_group" : param.get_backingStore_permissions_group(),
                            "b_p_mode" : param.get_backingStore_permissions_mode(),
                            "b_p_label" : param.get_backingStore_permissions_label(),
                            },
                "real" : {"dir" : real[0],
                          "name" : real[1],
                          "extension" : real[2],
                          },
                }


def getCredentials(credentials, data):

    userpass = data.split(":")

    for credential in credentials:

        if credential[0] == libvirt.VIR_CRED_AUTHNAME:
            credential[4] = userpass[0]

        elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
            credential[4] = userpass[1]

        else:
            return -1

    return 0


class KaresansuiVirtConnectionAuth(KaresansuiVirtConnection):

    def __init__(self,uri=None,creds="", readonly=True):
        self.logger = logging.getLogger('karesansui.virt')
        self.logger.debug(get_inspect_stack())
        try:
            self.open(uri, creds)
        except:
            raise KaresansuiVirtException(_("Cannot open '%s'") % uri_join(uri_split(uri.encode('utf8')), without_auth=True))

    def open(self, uri, creds="foo:pass"):
        """
        <comment-ja>
        libvirtのコネクションをOpenします。またそれに伴う初期化も行います。
        </comment-ja>
        <comment-en>
        </comment-en>
        """

        if uri != None:
            self.uri = uri

        try:
            self.logger.debug('libvirt.open - %s' % self.uri)

            flags = [libvirt.VIR_CRED_AUTHNAME,libvirt.VIR_CRED_PASSPHRASE]
            auth = [flags,getCredentials,creds]
            self._conn = libvirt.openAuth(self.uri,auth,0)

        except:
            self.logger.error('failed to libvirt open - %s' % self.uri)

        self.logger.debug('succeed to libvirt open - %s' % self.uri)

        self.guest = KaresansuiVirtGuest(self)

        return self._conn


if __name__ == '__main__':
    from karesansui.lib.utils import preprint_r

    conn = KaresansuiVirtConnection(readonly=False)
    try:
        pass
        #print conn.get_storage_pool_type("default")
        #preprint_r(conn.get_capabilities())
        #print conn.get_storage_pool_name_bydomain("test3-iscsi-1-mount.hoge.com",image_type='os')
        #print conn.get_storage_pool_name_bydomain("guest1",image_type='')
        #print conn.get_storage_pool_name_bydomain("centos55",image_type='')
        #print conn.get_storage_volume_bypool("default",attr="info")
        #print conn.get_storage_volume_bypool("default",attr="name")
        #print conn.get_storage_volume_bydomain("centos55",image_type=None, attr="name")
        #print conn.get_storage_volume_bydomain("centos55",image_type=None, attr="path")
        #print conn.get_storage_volume_bydomain("centos55",image_type="os", attr="info")
        #print conn.get_storage_volume_bydomain("centos55",image_type="os", attr="name")
        #print conn.get_storage_volume_bydomain("centos55",image_type="disk", attr="name")
        #print conn.get_storage_pool_name_byimage("/var/lib/libvirt/domains/guest1/images/guest1.img")
        #print conn.list_used_graphics_port()
        #print conn.list_used_mac_addr()

        #kvg = conn.search_kvg_guests("centos55")[0]
        #preprint_r(kvg.get_info())
        #preprint_r(kvg.get_disk_info())
        #conn.import_guest("/var/lib/libvirt/domains/527109d0-cb91-7308-ad39-7738c1893dc9", uuid=None, progresscb=None)
        #preprint_r(kvg.get_vcpus_info())
        #preprint_r(kvg.get_interface_info())
        #preprint_r(kvg.get_graphics_info())
        #print kvg.next_disk_target()
        #print kvg.delete_interface("52:54:00:0f:cb:6a")

        #kvn = conn.search_kvn_networks("default")[0]
        #preprint_r(kvn.get_info())

        #print conn.get_hypervisor_type()
        #print conn.get_hypervisor_type_bydomain("guest1")

    except:
        raise

