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
libvirtの仮想マシン(VM)の設定を生成する
</comment-ja>
<comment-en>
Generate configuration file of VMs for libvirt.
</comment-en>

@file:   config.py

@author: Taizo ITO <taizo@karesansui-project.info>

@copyright:    

"""

import time
import os, stat
import re
import shutil
from StringIO import StringIO
from xml.dom.ext import PrettyPrint
from xml.dom.DOMImplementation import implementation
import errno

import karesansui

from karesansui.lib.const import KARESANSUI_GROUP, VIRT_XML_CONFIG_DIR, \
                                 DEFAULT_KEYMAP

from karesansui.lib.const import XEN_VIRT_CONFIG_DIR, \
                                 XEN_KARESANSUI_TMP_DIR

from karesansui.lib.const import KVM_VIRT_CONFIG_DIR, \
                                 KVM_KARESANSUI_TMP_DIR

from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_nums_xml_xpath as XMLXpathNum, \
     get_xml_parse as XMLParse, \
     uniq_filename, r_chgrp, r_chmod, isset

from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.file.configfile import ConfigFile

SIZE_UNIT_MAP = { "b" : 1024**0, "k" : 1024**1, "m" : 1024**2, "g" : 1024**3 }
"""
<comment-ja>
ファイルサイズの単位とバイト数のマップを定義
</comment-ja>
<comment-en>
Define byte unit map
</comment-en>
"""

class KaresansuiConfigParamException(karesansui.KaresansuiLibException):
    pass

class ConfigParam:
    """
    <comment-ja>
    Xenの仮想マシン(VM)の設定ファイル(key = value形式)を生成するクラス
    </comment-ja>
    <comment-en>
    Class for generating Xen VM configuration file
    </comment-en>
    """

    def __init__(self, name):

        self.name = name
        self.domain_type = None
        self.os_root = None
        self.uuid = None
        self.kernel = None
        self.initrd = None
        self.boot_dev = None
        self.bootloader = None
        self.maxmem = None
        self.memory = None
        self.cmdline = []
        self.interfaces = []
        self.disks = []
        self.vcpus = 1
        self.max_vcpus = None
        self.vcpus_limit = None
        self.max_vcpus_limit = None
        self.graphic_type = "vnc"
        self.vnc_port = None
        self.vnc_autoport = "no"
        self.vnc_listen = None
        self.vnc_keymap = None
        self.vnc_passwd = None
        self.features_pae = None
        self.features_acpi = None
        self.features_apic = None
        self.behavior = { "on_poweroff" : "destroy",
                          "on_reboot"   : "restart",
                          "on_crash"    : "restart"
                        }
        self.current_snapshot = None
        self.config_file = None

    def __get_value(self,key):

        if self.domain_type == "xen":
            self.config_file = "%s/%s" % (XEN_VIRT_CONFIG_DIR, self.name)
        elif self.domain_type == "kvm":
            self.config_file = "%s/%s" % (KVM_VIRT_CONFIG_DIR, self.name)

        sh_regex = re.compile(r"""^(?P<key>[^ =]+) *= *[\"']?(?P<value>[^\"']*)[\"']?$""")
        ret = ''
        if os.path.exists(self.config_file):
            try:
                lines = ConfigFile(self.config_file).read()
                for line in lines:
                    line = line.strip()
                    if len(line) <= 0 or line[0] == "#":
                        continue
                    m = sh_regex.match(line)
                    if m and m.group('key') == key:
                        ret = m.group('value')
                        break
            except:
                ret = ''
        return ret

    def get_domain_name(self):
        return self.name

    def set_domain_type(self, domain_type):
        self.domain_type = domain_type

    def get_domain_type(self):
        return self.domain_type

    def set_os_root(self, os_root):
        self.os_root = os_root

    def get_os_root(self):
        return self.os_root

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_uuid(self):
        return self.uuid

    def set_current_snapshot(self, snapshot):
        if snapshot is not None:
            snapshot = str(snapshot)
        self.current_snapshot = snapshot

    def get_current_snapshot(self):
        return self.current_snapshot

    def set_behavior(self, param, value):
        self.behavior[param] = value

    def get_behavior(self, param):
        return self.behavior.get(param)

    def set_bootloader(self, bootloader):
        self.bootloader = bootloader

    def get_bootloader(self):
        return self.bootloader

    def set_kernel(self, kernel):
        self.kernel = kernel

    def get_kernel(self):
        return self.kernel

    def set_initrd(self, initrd):
        self.initrd = initrd

    def get_initrd(self):
        return self.initrd

    def set_boot_dev(self, boot_dev):
        self.boot_dev = boot_dev

    def get_boot_dev(self):
        return self.boot_dev

    def append_commandline(self, *args, **kwargs):
        for opt in args:
            self.cmdline.append(opt)
        for k,v in kwargs.iteritems():
            self.cmdline.append("%s=%s" % (k,v))

    def get_commandline(self):
        return " ".join(self.cmdline)

    def set_graphic_type(self, type):
        self.graphic_type = type

    def get_graphic_type(self):
        return self.graphic_type

    def set_vnc_port(self, port):
        self.vnc_port = port

    def get_vnc_port(self):
        return self.vnc_port

    def set_vnc_autoport(self, autoport):
        self.vnc_autoport = autoport

    def get_vnc_autoport(self):
        return self.vnc_autoport

    def set_vnc_listen(self, listen):
        self.vnc_listen = listen

    def get_vnc_listen(self):
        if self.vnc_listen == None:
            self.set_vnc_listen("0.0.0.0")
        return self.vnc_listen

    def set_vnc_keymap(self, keymap):
        self.vnc_keymap = keymap

    def get_vnc_keymap(self):
        #if self.vnc_keymap == None:
        #    self.set_vnc_keymap(DEFAULT_KEYMAP)
        return self.vnc_keymap

    def set_vnc_passwd(self, passwd):
        self.vnc_passwd = passwd
    def get_vnc_passwd(self):
        return self.vnc_passwd

    def set_vcpus(self, vcpus):
        self.vcpus = vcpus
    def get_vcpus(self):
        return self.vcpus

    def set_max_vcpus(self, max_vcpus):
        self.max_vcpus = max_vcpus

    def get_max_vcpus(self):
        return self.max_vcpus

    def set_vcpus_limit(self, vcpus_limit):
        self.vcpus_limit = vcpus_limit

    def get_vcpus_limit(self):
        return self.vcpus_limit

    def set_max_vcpus_limit(self, max_vcpus_limit):
        self.max_vcpus_limit = max_vcpus_limit

    def get_max_vcpus_limit(self):
        return self.max_vcpus_limit

    def set_features_pae(self, pae):
        self.features_pae = pae

    def get_features_pae(self):
        return self.features_pae

    def set_features_acpi(self, acpi):
        self.features_acpi = acpi

    def get_features_acpi(self):
        return self.features_acpi

    def set_features_apic(self, apic):
        self.features_apic = apic

    def get_features_apic(self):
        return self.features_apic

    def add_disk(self, path, target, device="disk",
                 bus="ide", disk_type="file", driver_name=None, driver_type=None, shareable=None, readonly=None):
        disk = {"path"     :path,
                "target"   :target,
                "device"   :device,
                "bus"      :bus,
                "disk_type":str(disk_type),
                "shareable":shareable,
                "readonly" :readonly,
                }

        if driver_name is not None:
            disk["driver_name"] = str(driver_name)

        if driver_type is not None:
            disk["driver_type"] = str(driver_type)

        self.disks.append(disk)

    def delete_disk(self, target):
        for arr in self.disks:
            if arr["target"] == target:
                self.disks.remove(arr)

    def get_disk(self):
        return self.disks

    def get_disk_path(self,target):
        for arr in self.disks:
            if arr["target"] == target:
                return arr["path"]
        return None

    def add_interface(self, mac, type, bridge, script, target=None, model=None):
        self.interfaces.append( {"mac": mac, "type": type, "bridge": bridge, "script": script, "target": target, "model": model} )

    def delete_interface(self, mac):
        for arr in self.interfaces:
            if arr["mac"] == mac:
                self.interfaces.remove(arr)

    def get_interface(self):
        return self.interfaces

    def set_memory(self, memory):
        try:
            memory = str(memory).strip().lower()
        except Exception, e:
            param_err = KaresansuiConfigParamException("invalid memory: %s" % str(memory))
            param_err.exception = e
        p = re.compile(r"""^(?P<bytes>\d+)(?P<unit>[gmkb]?)$""")
        m = p.match(memory)
        if not m: raise KaresansuiConfigParamException("invalid memory: %s" % str(memory))

        self.memory = int(m.group("bytes")) * SIZE_UNIT_MAP.get(m.group("unit"), 1)
        if (self.memory <= 0): raise KaresansuiConfigParamException("invalid memory: %d" % self.memory)
        
    def get_memory(self, unit="b"):
        if not unit in SIZE_UNIT_MAP.keys():
            raise KaresansuiConfigParamException("no such unit: %s" % unit)
        return int(self.memory / SIZE_UNIT_MAP.get(unit))

    def set_max_memory(self, memory):
        try:
            memory = str(memory).strip().lower()
        except Exception, e:
            param_err = KaresansuiConfigParamException("invalid memory: %s" % str(memory))
            param_err.exception = e
        import re
        p = re.compile(r"""^(?P<bytes>\d+)(?P<unit>[gmkb]?)$""")
        m = p.match(memory)
        if not m: raise KaresansuiConfigParamException("invalid memory: %s" % str(memory))

        self.maxmem = int(m.group("bytes")) * SIZE_UNIT_MAP.get(m.group("unit"), 1)
        if (self.maxmem <= 0): raise KaresansuiConfigParamException("invalid memory: %d" % self.maxmem)
        
    def get_max_memory(self, unit="b"):
        if self.maxmem == None and self.memory != None:
            self.maxmem = self.memory
        if not unit in SIZE_UNIT_MAP.keys():
            raise KaresansuiConfigParamException("no such unit: %s" % unit)
        return int(self.maxmem / SIZE_UNIT_MAP.get(unit))

    def load_xml_config(self,path):

        #if not os.path.exists(path):
        #    raise KaresansuiConfigParamException("no such file: %s" % path)

        document = XMLParse(path)

        domain_type = XMLXpath(document,'/domain/@type')
        self.set_domain_type(str(domain_type))

        os_root = XMLXpath(document,'/domain/os/root/text()')
        if os_root:
            self.set_os_root(str(os_root))

        uuid = XMLXpath(document,'/domain/uuid/text()')
        self.set_uuid(str(uuid))

        current_snapshot = XMLXpath(document,'/domain/currentSnapshot/text()')
        if current_snapshot:
            self.set_current_snapshot(str(current_snapshot))

        bootloader = XMLXpath(document,'/domain/bootloader/text()')
        if bootloader:
            self.set_bootloader(str(bootloader))

        kernel = XMLXpath(document,'/domain/os/kernel/text()')
        if kernel:
            self.set_kernel(str(kernel))

        initrd = XMLXpath(document,'/domain/os/initrd/text()')
        if initrd:
            self.set_initrd(str(initrd))

        boot_dev = XMLXpath(document,'/domain/os/boot/@dev')
        if boot_dev:
            self.set_boot_dev(str(boot_dev))

        features_pae = XMLXpathNum(document,'/domain/features/pae')
        if features_pae > 0:
            self.set_features_pae(True)

        features_acpi = XMLXpathNum(document,'/domain/features/acpi')
        if features_acpi > 0:
            self.set_features_acpi(True)

        features_apic = XMLXpathNum(document,'/domain/features/apic')
        if features_apic > 0:
            self.set_features_apic(True)

        memory = XMLXpath(document,'/domain/memory/text()')
        if memory:
            self.set_memory(memory+"k")

        maxmem = XMLXpath(document,'/domain/maxmem/text()')
        if maxmem:
            self.set_max_memory(maxmem+"k")

        max_vcpu = XMLXpath(document,'/domain/vcpu/text()')
        self.set_max_vcpus(int(max_vcpu))

        graphic_type = XMLXpath(document,'/domain/devices/graphics/@type')
        self.set_graphic_type(str(graphic_type))

        vnc_port = XMLXpath(document,'/domain/devices/graphics/@port')
        self.set_vnc_port(int(vnc_port))

        vnc_autoport = XMLXpath(document,'/domain/devices/graphics/@autoport')
        self.set_vnc_autoport(str(vnc_autoport))

        vnc_listen = XMLXpath(document,'/domain/devices/graphics/@listen')
        if vnc_listen:
            self.set_vnc_listen(str(vnc_listen))

        vnc_keymap = XMLXpath(document,'/domain/devices/graphics/@keymap')
        if vnc_keymap:
            self.set_vnc_keymap(str(vnc_keymap))

        vnc_passwd = XMLXpath(document,'/domain/devices/graphics/@passwd')
        if vnc_passwd:
            self.set_vnc_passwd(str(vnc_passwd))
        else:
            vnc_passwd = self.__get_value('vncpasswd')
            if vnc_passwd != "":
                self.set_vnc_passwd(vnc_passwd)

        self.interfaces = []
        interface_num = XMLXpathNum(document,'/domain/devices/interface')
        for n in range(1, interface_num + 1):
            type = XMLXpath(document,'/domain/devices/interface[%i]/@type' % n)
            mac = XMLXpath(document,'/domain/devices/interface[%i]/mac/@address' % n)
            if str(type) == "network":
                name = XMLXpath(document,'/domain/devices/interface[%i]/source/@network' % n)
            else:
                name = XMLXpath(document,'/domain/devices/interface[%i]/source/@bridge' % n)
            script = XMLXpath(document,'/domain/devices/interface[%i]/script/@path' % n)
            if script != None:
                script = str(script)
            target = XMLXpath(document,'/domain/devices/interface[%i]/target/@dev' % n)
            if target != None:
                target = str(target)
            model = XMLXpath(document,'/domain/devices/interface[%i]/model/@type' % n)
            if model != None:
                model = str(model)
            self.add_interface(str(mac), str(type), str(name), script, target, model=model)

        self.disks = []
        disk_num = XMLXpathNum(document,'/domain/devices/disk')
        for n in range(1, disk_num + 1):
            device_type = XMLXpath(document,'/domain/devices/disk[%i]/@device' % n)
            if device_type == None:
                device_type = "disk"
            disk_type = XMLXpath(document,'/domain/devices/disk[%i]/@type' % n)
            source_dev = XMLXpath(document,'/domain/devices/disk[%i]/source/@dev' % n) # block
            source_file = XMLXpath(document,'/domain/devices/disk[%i]/source/@file' % n) # file
            if source_dev:
                source_attribute = source_dev
            elif source_file:
                source_attribute = source_file

            target_dev = XMLXpath(document,'/domain/devices/disk[%i]/target/@dev' % n)
            target_bus = XMLXpath(document,'/domain/devices/disk[%i]/target/@bus' % n)

            driver_name = XMLXpath(document,'/domain/devices/disk[%i]/driver/@name' % n)
            driver_type = XMLXpath(document,'/domain/devices/disk[%i]/driver/@type' % n)

            shareable = None
            shareable_num = XMLXpathNum(document,'/domain/devices/disk[%i]/shareable' % n)
            if shareable_num > 0:
                shareable = True

            readonly = None
            readonly_num = XMLXpathNum(document,'/domain/devices/disk[%i]/readonly' % n)
            if readonly_num > 0:
                readonly = True

            if target_bus is None:
                self.add_disk(str(source_attribute),
                              str(target_dev),
                              device=str(device_type),
                              disk_type=disk_type,
                              driver_name=driver_name,
                              driver_type=driver_type,
                              shareable=shareable,
                              readonly=readonly,
                              )
            else:
                self.add_disk(str(source_attribute),
                              str(target_dev),
                              device=str(device_type),
                              bus=str(target_bus),
                              disk_type=disk_type,
                              driver_name=driver_name,
                              driver_type=driver_type,
                              shareable=shareable,
                              readonly=readonly,
                              )

        on_poweroff = XMLXpath(document,'/domain/on_poweroff/text()')
        if on_poweroff:
            self.set_behavior('on_poweroff',str(on_poweroff))
        on_reboot = XMLXpath(document,'/domain/on_reboot/text()')
        if on_reboot:
            self.set_behavior('on_reboot',str(on_reboot))
        on_crash = XMLXpath(document,'/domain/on_crash/text()')
        if on_crash:
            self.set_behavior('on_crash',str(on_crash))


    def validate(self):

        if not self.uuid:
            raise KaresansuiConfigParamException("ConfigParam: uuid is None")
        if self.vnc_port < 5900:
            raise KaresansuiConfigParamException("ConfigParam: vnc port < 5900: %d" % self.vnc_port)
        if self.vcpus < 1:
            raise KaresansuiConfigParamException("ConfigParam: vcpus < 1: %d" % self.vcpus)
        if self.vcpus_limit and self.vcpus_limit < self.vcpus:
            raise KaresansuiConfigParamException("ConfigParam: vcpus > %d: %d" % (self.vcpus_limit, self.vcpus))
        if self.max_vcpus is not None and self.max_vcpus < 1:
            raise KaresansuiConfigParamException("ConfigParam: max_vcpus < 1: %d" % self.max_vcpus)
        if self.max_vcpus is not None and self.max_vcpus_limit and self.max_vcpus_limit < self.max_vcpus:
            raise KaresansuiConfigParamException("ConfigParam: max_vcpus > %d: %d" %(self.max_vcpus_limit, self.max_vcpus))
        if self.bootloader and not os.path.exists(self.bootloader):
            raise KaresansuiConfigParamException("ConfigParam: bootloader %s not found", self.bootloader)
        #if self.kernel and not os.path.exists(self.kernel):
        #    raise KaresansuiConfigParamException("ConfigParam: kernel %s not found", self.kernel)
        #if self.initrd and not os.path.exists(self.initrd):
        #    raise KaresansuiConfigParamException("ConfigParam: initrd %s not found", self.initrd)
        if not len(self.get_disk()):
            raise KaresansuiConfigParamException("ConfigParam: no disks are specified")
        if not self.name or not len(self.name):
            raise KaresansuiConfigParamException("ConfigParam: illegal name")
        """
        if not len(self.get_interface()):
            raise KaresansuiConfigParamException("ConfigParam: no interfaces are specified")
        """

class XMLGenerator:

    def _create_text_node(self, tag, txt):
        node = self.document.createElement(tag)
        if txt is not None:
            self._add_text(node, txt)
        return node

    def _add_text(self, node, txt):
        txt_n = self.document.createTextNode(txt)
        node.appendChild(txt_n)

    def generate(self, config):
        tree = self.generate_xml_tree(config)
        out = StringIO()
        PrettyPrint(tree, out)
        return out.getvalue()

class ConfigGenerator:

    def __init__(self,domain_type):
      self.config_dir = KVM_VIRT_CONFIG_DIR
      if domain_type == "xen":
        self.config_dir = XEN_VIRT_CONFIG_DIR
      elif domain_type == "kvm":
        self.config_dir = KVM_VIRT_CONFIG_DIR

    def generate(self, config):
        config.validate()
        self.config = config
        
        self.out = StringIO()
        self.print_header()
        self.print_bootloader_section()
        self.print_kernel_section()
        self.print_disks_section()
        self.print_memory_section()
        self.print_vcpu_section()
        self.print_vnc_section()
        self.print_network_section()
        self.print_behavior_section()
        return self.out.getvalue()

    def _print_param(self, key, value):
        if value != '':
            print >>self.out, key, "=", "%s" % repr(value)

    def print_header(self):
        print >>self.out, "# This is an automatically generated xen configuration file: %s" % self.config.get_domain_name()
        print >>self.out, "# Generated Date: %s" % time.ctime()
        print >>self.out
        self._print_param("name", self.config.get_domain_name())
        self._print_param("uuid", self.config.get_uuid())
        if self.config.get_current_snapshot() is not None:
            self._print_param("current_snapshot", self.config.get_current_snapshot())
        print >>self.out

    def print_kernel_section(self):
        print >>self.out, "# Kernel configuration"
        if self.config.get_kernel():
            self._print_param("kernel", self.config.get_kernel())
        if self.config.get_initrd():
            self._print_param("ramdisk", self.config.get_initrd())
        # additional arguments to kernel
        if self.config.get_commandline():
            self._print_param("extra", self.config.get_commandline())
        if self.config.get_features_pae() is True:
            self._print_param("pae", 1)
        if self.config.get_features_acpi() is True:
            self._print_param("acpi", 1)
        if self.config.get_features_apic() is True:
            self._print_param("apic", 1)
        print >>self.out

    def print_bootloader_section(self):
        print >>self.out, "# Bootloader configuration"
        if self.config.get_bootloader():
            self._print_param("bootloader", self.config.get_bootloader())
        print >>self.out

    def print_memory_section(self):
        print >>self.out, "# Memory configuration"
        self._print_param("maxmem", self.config.get_max_memory("m"))
        self._print_param("memory", self.config.get_memory("m"))
        print >>self.out

    def print_vcpu_section(self):
        print >>self.out, "# CPU configuration"
        self._print_param("vcpus", self.config.get_max_vcpus())
        print >>self.out

    def print_disks_section(self):
        
        print >>self.out, "# Disk device configuration"
        
        # root
        self._print_param("root", "/dev/"+self.config.get_disk()[0]["target"])

        # all disks
        disks = []
        for disk in self.config.get_disk():
            if stat.S_ISBLK(os.stat(disk['path'])[stat.ST_MODE]):
                ftype = "phy"
            else:
                ftype = "file"
            disk_param = ftype+":%(path)s,%(target)s,w" % disk
            disks.append( str(disk_param) )
        self._print_param("disk", disks)
        print >>self.out

    def print_network_section(self):
        print >>self.out, "# Network configuration"
        vif = []
        for interface in self.config.get_interface():
            vif_param = "mac=%(mac)s, bridge=%(bridge)s" % interface
            vif.append( str(vif_param) )
        self._print_param("vif", vif)
        print >>self.out

    def print_vnc_section(self):
        print >>self.out, "# Graphics configuration"
        if self.config.get_vnc_port():
            if self.config.get_graphic_type() == "sdl":
                self._print_param("sdl", 1)
                self._print_param("vnc", 0)
            else:
                self._print_param("sdl", 0)
                self._print_param("vnc", 1)
            self._print_param("vncunused", 0)
            self._print_param("vncdisplay", int(self.config.get_vnc_port())-5900)
            self._print_param("vnclisten", self.config.get_vnc_listen())
            if self.config.get_vnc_keymap() is not None:
                self._print_param("keymap", self.config.get_vnc_keymap())
            if self.config.get_vnc_passwd() is not None and self.config.get_vnc_passwd() != "":
                self._print_param("vncpasswd", self.config.get_vnc_passwd())
        print >>self.out

    def print_behavior_section(self):
        print >>self.out, "# Behavior configuration"
        self._print_param("on_poweroff", self.config.get_behavior("on_poweroff"))
        self._print_param("on_reboot", self.config.get_behavior("on_reboot"))
        self._print_param("on_crash", self.config.get_behavior("on_crash"))

    def writecfg(self,cfg, config_dir=None):
        if config_dir is None:
            config_dir = self.config_dir
            
        filename = "%s/%s" %(config_dir, self.config.get_domain_name())
        ConfigFile(filename).write(cfg)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

    def copycfg(self,src_dir):
            
        src_filename = "%s/%s" %(src_dir, self.config.get_domain_name())
        filename = "%s/%s" %(self.config_dir, self.config.get_domain_name())
        
        shutil.copy(src_filename, filename)
        
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

    def removecfg(self, config_dir=None):
        if config_dir is None:
            config_dir = self.config_dir

        filename = "%s/%s" %(config_dir, self.config.get_domain_name())
        if os.path.exists(filename):
            os.unlink(filename)
 
class XMLDiskConfigGenerator(XMLGenerator):

    def __init__(self):
        self.path = None
        self.target = None
        self.bus = None

    def set_path(self, path):
        self.path = path
    def get_path(self):
        return self.path

    def set_target(self, target):
        self.target = target
    def get_target(self):
        return self.target

    def set_bus(self, bus):
        self.bus = bus
    def get_bus(self):
        return self.bus

    def validate(self):
        pass #TODO

    def generate_xml_tree(self, config=None):
#        self.validate()

        self.begin_build()
        self.build_disk()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.disk = self.document.createElement("disk")

        self.disk.setAttribute("type", "file")
        self.disk.setAttribute("device", "disk")

        self.document.appendChild(self.disk)

    def build_disk(self):
        doc = self.document
        driver = doc.createElement("driver")
        driver.setAttribute("name", "file")
        self.disk.appendChild(driver)

        # TODO
        if self.get_path() != None:
            source = doc.createElement("source")
            source.setAttribute("file", self.get_path())
            self.disk.appendChild(source)

        if self.get_target() != None:
            target = doc.createElement("target")
            target.setAttribute("dev", self.get_target())
            if self.get_bus() != None:
                target.setAttribute("bus", self.get_bus())
            self.disk.appendChild(target)

    def end_build(self):
        pass

class XMLInterfaceConfigGenerator(XMLGenerator):

    def __init__(self):
        self.mac = None
        self.bridge = None
        self.script = None
        self.target = None

    def set_mac(self, mac):
        self.mac = mac
    def get_mac(self):
        return self.mac

    def set_bridge(self, bridge):
        self.bridge = bridge
    def get_bridge(self):
        return self.bridge

    def set_script(self, script):
        self.script = script
    def get_script(self):
        return self.script

    def set_target(self, target):
        self.target = target
    def get_target(self):
        return self.target

    def validate(self):
        if not os.path.exists("/etc/xen/scripts/" + self.script):
            raise KaresansuiConfigParamException("ConfigParam: script %s not found", self.path)

    def generate_xml_tree(self, config=None):
#        self.validate()

        self.begin_build()
        self.build_interface()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.interface = self.document.createElement("interface")

        self.interface.setAttribute("type", "bridge")
        self.document.appendChild(self.interface)

    def build_interface(self):
        doc = self.document

        if self.get_mac():
            mac = doc.createElement("mac")
            mac.setAttribute("address", self.get_mac())
            self.interface.appendChild(mac)

        if self.get_bridge():
            source = doc.createElement("source")
            source.setAttribute("bridge", self.get_bridge())
            self.interface.appendChild(source)

        if self.get_script():
            script = doc.createElement("script")
            script.setAttribute("path", self.get_script())
            self.interface.appendChild(script)

        if self.get_target():
            target = doc.createElement("target")
            target.setAttribute("dev", self.get_target())
            self.interface.appendChild(target)

    def end_build(self):
        pass

class XMLGraphicsConfigGenerator(XMLGenerator):

    def __init__(self):
        self.port = None
        self.listen = None
        self.keymap = None

    def set_port(self, port):
        self.port = port
    def get_port(self):
        if self.port == None:
          self.set_port(5901)
        return self.port

    def set_listen(self, listen):
        self.listen = listen
    def get_listen(self):
        if self.listen is None:
          self.set_listen("0.0.0.0")
        return self.listen

    def set_keymap(self, keymap):
        self.keymap = keymap
    def get_keymap(self):
        #if self.keymap is None:
        #  self.set_keymap(DEFAULT_KEYMAP)
        return self.keymap

    def validate(self):
        if self.get_port() < 5900:
            raise KaresansuiConfigParamException("ConfigParam: port < 5900: %d" % self.get_port())

    def generate_xml_tree(self, config=None):
        self.validate()
        self.build_graphics()
        return self.document

    def build_graphics(self):
        self.document = implementation.createDocument(None,None,None)
        self.graphics = self.document.createElement("graphics")

        self.graphics.setAttribute("type", "vnc")
        self.graphics.setAttribute("port", str(self.get_port()))
        self.graphics.setAttribute("listen", self.get_listen())
        if self.get_keymap() is not None:
            self.graphics.setAttribute("keymap", self.get_keymap())
        self.document.appendChild(self.graphics)

class XMLConfigGenerator(XMLGenerator):

    def __init__(self):
        self.config_dir = VIRT_XML_CONFIG_DIR

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config

        self.begin_build()
        self.build_os()
        self.build_features()
        self.build_other()
        self.build_devices()
        self.build_behavior()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.domain = self.document.createElement("domain")

        self.domain.setAttribute("type", self.config.get_domain_type())
        name = self._create_text_node("name", self.config.get_domain_name())
        uuid = self._create_text_node("uuid", self.config.get_uuid())
        self.domain.appendChild(name)
        self.domain.appendChild(uuid)
        if self.config.get_current_snapshot():
            current_snapshot = self._create_text_node("currentSnapshot", self.config.get_current_snapshot())
            self.domain.appendChild(current_snapshot)

        self.document.appendChild(self.domain)

    def build_os(self):
        doc = self.document
        os_elem = doc.createElement("os")

        if self.config.get_domain_type() == "kvm":
            type_n = self._create_text_node("type", "hvm")
            type_n.setAttribute("arch", os.uname()[4])
            type_n.setAttribute("machine", "pc")
        else:
            type_n = self._create_text_node("type", "linux")
        os_elem.appendChild(type_n)

        if self.config.get_kernel():
            os_elem.appendChild(self._create_text_node("kernel", self.config.get_kernel()))
        if self.config.get_initrd():
            os_elem.appendChild(self._create_text_node("initrd", self.config.get_initrd()))
        os_elem.appendChild(self._create_text_node("root", "/dev/" + self.config.get_disk()[0]["target"]))

        if self.config.get_boot_dev():
            boot_dev_n = doc.createElement("boot")
            boot_dev_n.setAttribute("dev", self.config.get_boot_dev())
            os_elem.appendChild(boot_dev_n)

        # additional commandline
        if self.config.get_commandline():
            os_elem.appendChild(self._create_text_node("cmdline", self.config.get_commandline()))

        self.domain.appendChild(os_elem)

    def build_features(self):
        doc = self.document
        if self.config.get_features_pae()  is True or \
           self.config.get_features_acpi() is True or \
           self.config.get_features_apic() is True:

            features_elem = doc.createElement("features")

            if self.config.get_features_pae() is True:
                features_elem.appendChild(self._create_text_node("pae",None))

            if self.config.get_features_acpi() is True:
                features_elem.appendChild(self._create_text_node("acpi",None))

            if self.config.get_features_apic() is True:
                features_elem.appendChild(self._create_text_node("apic",None))

            self.domain.appendChild(features_elem)

    def build_other(self):
        self.domain.appendChild(self._create_text_node("maxmem",
                                    str(self.config.get_max_memory("k"))))
        self.domain.appendChild(self._create_text_node("memory",
                                    str(self.config.get_memory("k"))))
        self.domain.appendChild(self._create_text_node("vcpu",
                                    str(self.config.get_max_vcpus())))
        if self.config.get_bootloader():
            self.domain.appendChild(self._create_text_node("bootloader",
                                        str(self.config.get_bootloader())))

    def build_devices(self):
        doc = self.document
        devs_elem = doc.createElement("devices")

        # graphics
        if self.config.get_vnc_port():
            graphics_n = doc.createElement("graphics")
            if self.config.get_graphic_type() == "sdl":
                graphics_n.setAttribute("type", "sdl")
            else:
                graphics_n.setAttribute("type", "vnc")
            graphics_n.setAttribute("port", str(self.config.get_vnc_port()))
            graphics_n.setAttribute("autoport", str(self.config.get_vnc_autoport()))
            graphics_n.setAttribute("listen", str(self.config.get_vnc_listen()))
            if self.config.get_vnc_keymap() is not None:
                graphics_n.setAttribute("keymap", str(self.config.get_vnc_keymap()))
            if self.config.get_vnc_passwd() is not None:
                graphics_n.setAttribute("passwd", str(self.config.get_vnc_passwd()))
            devs_elem.appendChild(graphics_n)

        # disks
        for disk in self.config.get_disk():
            disk_n = doc.createElement("disk")

            if disk["disk_type"] == "file":
                disk_n.setAttribute("type", "file")
            elif disk["disk_type"] == "block":
                disk_n.setAttribute("type", "block")
            else:
                disk_n.setAttribute("type", "file") # default                
                
            disk_n.setAttribute("device", disk["device"])

            # disk -> driver
            driver_n = doc.createElement("driver")
            try:
                if disk["driver_name"] is not None:
                    driver_n.setAttribute("name", disk["driver_name"])
            except:
                pass
            try:
                if disk["driver_type"] is not None:
                    driver_n.setAttribute("type", disk["driver_type"])
            except:
                pass

            source_n = doc.createElement("source")
            if disk["disk_type"] == "file":
                source_n.setAttribute("file", disk["path"])
            elif disk["disk_type"] == "block":
                source_n.setAttribute("dev", disk["path"])
            else:
                source_n.setAttribute("file", disk["path"]) # default
                
            target_n = doc.createElement("target")
            target_n.setAttribute("dev", disk["target"])
            if disk["bus"] != None:
                target_n.setAttribute("bus", disk["bus"])

            disk_n.appendChild(driver_n)
            disk_n.appendChild(source_n)
            disk_n.appendChild(target_n)

            #if isset("disk['shareable']",vars=locals()) is True:
            #    disk_n.appendChild(self._create_text_node("shareable",None))

            #if isset("disk['readonly']",vars=locals()) is True:
            #    disk_n.appendChild(self._create_text_node("readonly",None))

            devs_elem.appendChild(disk_n)

        # network
        for interface in self.config.get_interface():

            interface_n = doc.createElement("interface")
            interface_n.setAttribute("type", "bridge")
            
            source_n = doc.createElement("source")
            source_n.setAttribute("bridge", interface["bridge"])
            mac_n = doc.createElement("mac")
            mac_n.setAttribute("address", interface["mac"])
            interface_n.appendChild(source_n)
            interface_n.appendChild(mac_n)
            if interface["script"] != None:
                script_n = doc.createElement("script")
                script_n.setAttribute("path", interface["script"])
                interface_n.appendChild(script_n)
            if interface["target"] != None:
                target_n = doc.createElement("target")
                target_n.setAttribute("dev", interface["target"])
                interface_n.appendChild(target_n)
            if interface["model"] != None:
                model_n = doc.createElement("model")
                model_n.setAttribute("type", interface["model"])
                interface_n.appendChild(model_n)
            devs_elem.appendChild(interface_n)
        
        self.domain.appendChild(devs_elem)

    def build_behavior(self):
        self.domain.appendChild(self._create_text_node("on_poweroff",
                                    self.config.get_behavior("on_poweroff")))
        self.domain.appendChild(self._create_text_node("on_reboot",
                                    self.config.get_behavior("on_reboot")))
        self.domain.appendChild(self._create_text_node("on_crash",
                                    self.config.get_behavior("on_crash")))

    def end_build(self):
        pass

    def writecfg(self,cfg,config_dir=None):
        if config_dir is None:
            config_dir = self.config_dir
        try:
            os.makedirs(config_dir)
        except OSError, (err, msg):
            if err != errno.EEXIST:
                raise OSError(err,msg)
        filename = "%s/%s.xml" %(config_dir,self.config.get_domain_name())
        ConfigFile(filename).write(cfg)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

    def copycfg(self,src_dir):
        try:
            os.makedirs(self.config_dir)
        except OSError, (err, msg):
            if err != errno.EEXIST:
                raise OSError(err,msg)
            
        src_filename = "%s/%s.xml" %(src_dir ,self.config.get_domain_name())
        filename = "%s/%s.xml" %(self.config_dir,self.config.get_domain_name())
        
        shutil.copy(src_filename, filename)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

    def removecfg(self, config_dir=None):
        if config_dir is None:
            config_dir = self.config_dir

        filename = "%s/%s.xml" %(config_dir,self.config.get_domain_name())
        if os.path.exists(filename):
            os.unlink(filename)

def sync_config_generator(param, domname=None):

    domain_type = param.get_domain_type()

    tmp_prefix = KVM_KARESANSUI_TMP_DIR
    if domain_type == "xen":
      tmp_prefix = XEN_KARESANSUI_TMP_DIR
    elif domain_type == "kvm":
      tmp_prefix = KVM_KARESANSUI_TMP_DIR

    if os.path.exists(tmp_prefix) is False:
        os.makedirs(tmp_prefix)

    uniq = uniq_filename()

    tmp_dir = "%s/%s" % (tmp_prefix, uniq)
    tmp_xml_dir = "%s/%s/xml" % (tmp_prefix, uniq)

    if os.path.exists(tmp_dir) is False:
        os.makedirs(tmp_dir)
    if os.path.exists(tmp_xml_dir) is False:
        os.makedirs(tmp_xml_dir)

    # config
    config_generator = ConfigGenerator(domain_type)
    cfg = config_generator.generate(param)

    # xml config
    xml_generator = XMLConfigGenerator()
    cfgxml = xml_generator.generate(param)

    try:
        config_generator.writecfg(cfg, tmp_dir)
        xml_generator.writecfg(cfgxml, tmp_xml_dir)
    except:
        config_generator.removecfg(tmp_dir)
        xml_generator.removecfg(tmp_xml_dir)
        raise KaresansuiConfigParamException("Failed to update tmp configuration files. - domname=" + str(domname))

    try:
        config_generator.copycfg(tmp_dir)
        xml_generator.copycfg(tmp_xml_dir)
    except:
        raise KaresansuiConfigParamException("Failed to update configuration files. - domname=" + str(domname))

    return True
