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
</comment-ja>
<comment-en>
Read xml of libvirt's capabilities and load to object.
!!! Notice: this is read-only parser. !!!
</comment-en>

@file:   config_capabilities.py

@author: Taizo ITO <taizo@karesansui-project.info>

xml sample:
-----------------------------------------------------------
<capabilities>
  <host>
    <cpu>
      <arch>x86_64</arch>
      <model>pentium3</model>
      <topology sockets='1' cores='1' threads='1'/>
      <feature name='syscall'/>
      <feature name='hypervisor'/>
      <feature name='acpi'/>
      <feature name='apic'/>
    </cpu>
    <migration_features>
      <live/>
      <uri_transports>
        <uri_transport>tcp</uri_transport>
      </uri_transports>
    </migration_features>
  </host>
  <guest>
    <os_type>hvm</os_type>
    <arch name='i686'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu</emulator>
      <machine>pc-0.12</machine>
      <machine canonical='pc-0.12'>pc</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
    <features>
      <cpuselection/>
      <pae/>
      <nonpae/>
      <acpi default='on' toggle='yes'/>
      <apic default='on' toggle='no'/>
    </features>
  </guest>
  <guest>
    <os_type>hvm</os_type>
    <arch name='x86_64'>
      <wordsize>64</wordsize>
      <emulator>/usr/bin/qemu-system-x86_64</emulator>
      <machine>pc-0.12</machine>
      <machine canonical='pc-0.12'>pc</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
    <features>
      <cpuselection/>
      <acpi default='on' toggle='yes'/>
      <apic default='on' toggle='no'/>
    </features>
  </guest>
</capabilities>
-----------------------------------------------------------

"""

import os
import time

from StringIO import StringIO
import errno

import karesansui

from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_nums_xml_xpath as XMLXpathNum, \
     get_xml_parse as XMLParse, \
     r_chgrp, r_chmod, preprint_r

class KaresasnuiCapabilitiesConfigParamException(karesansui.KaresansuiLibException):
    pass

class CapabilitiesConfigParam:

    def __init__(self):
        self.host      = {}
        self.guest     = []

    def get_host_cpu_arch(self):
        try:
            return self.host['cpu']['arch']
        except:
            return None

    def load_xml_config(self,string):

        doc = XMLParse(string)
        xpath_prefix = "/capabilities"

        ###################
        # host section
        host_xpath = "%s/host" % xpath_prefix
        host = {}

        # host - cpu section
        host_cpu_xpath = "%s/cpu" % host_xpath
        cpu = {}
        cpu['arch']  = XMLXpath(doc, '%s/arch/text()'  % host_cpu_xpath)
        cpu['model'] = XMLXpath(doc, '%s/model/text()' % host_cpu_xpath)
        topology = {}
        topology['sockets'] = XMLXpath(doc, '%s/topology/@sockets' % host_cpu_xpath)
        topology['cores']   = XMLXpath(doc, '%s/topology/@cores'   % host_cpu_xpath)
        topology['threads'] = XMLXpath(doc, '%s/topology/@threads' % host_cpu_xpath)
        cpu['topology'] = topology

        features = {}
        feature = []
        feature_num = XMLXpathNum(doc, '%s/feature' % host_cpu_xpath)
        for n in range(1, feature_num + 1):
            name = XMLXpath(doc, '%s/feature[%i]/@name' % (host_cpu_xpath, n,))
            feature.append(name)
        vmx = XMLXpath(doc, '%s/features/vmx' % host_cpu_xpath)
        features['feature'] = feature
        features['vmx'] = vmx
        cpu['feature'] = features

        host['cpu'] = cpu

        # host - migration_features section
        host_migration_features_xpath = "%s/migration_features" % host_xpath
        migration_features = {}

        uri_transports = []
        uri_transport_num = XMLXpathNum(doc,'%s/uri_transports/uri_transport' % host_migration_features_xpath)
        for n in range(1, uri_transport_num + 1):
            uri_transport = XMLXpath(doc,'%s/uri_transports/uri_transport/text()' % host_migration_features_xpath)
            uri_transports.append(uri_transport)
        live = XMLXpath(doc, '%s/live' % host_migration_features_xpath)
        migration_features['uri_transports'] = uri_transports
        migration_features['live'] = live

        host['migration_features'] = migration_features

        ###################
        # guest section
        guest_xpath = "%s/guest" % xpath_prefix
        guests = []

        guest_num = XMLXpathNum(doc,'%s' % guest_xpath)
        for n in range(1, guest_num + 1):
            guest = {}

            os_type  = XMLXpath(doc, '%s[%i]/os_type/text()' % (guest_xpath,n,))

            arch = {}
            name     = XMLXpath(doc, '%s[%i]/arch/@name'           % (guest_xpath,n,))
            wordsize = XMLXpath(doc, '%s[%i]/arch/wordsize/text()' % (guest_xpath,n,))
            emulator = XMLXpath(doc, '%s[%i]/arch/emulator/text()' % (guest_xpath,n,))
            machines = []
            machine_num = XMLXpathNum(doc, '%s[%i]/arch/machine'      % (guest_xpath,n,))
            for m in range(1, machine_num + 1):
                machine = XMLXpath(doc, '%s[%i]/arch/machine[%i]/text()'  % (guest_xpath,n,m,))
                machines.append(machine)
            domain = {}
            type = XMLXpath(doc, '%s[%i]/arch/domain/@type'        % (guest_xpath,n,))
            domain['type'] = type
            arch['name'] = name
            arch['wordsize'] = wordsize
            arch['emulator'] = emulator
            arch['machine']  = machines
            arch['domain']   = domain

            features = {}
            cpuselection  = XMLXpath(doc, '%s[%i]/features/cpuselection' % (guest_xpath,n,))
            pae      = XMLXpath(doc, '%s[%i]/features/pae'           % (guest_xpath,n,))
            nonpae   = XMLXpath(doc, '%s[%i]/features/nonpae'        % (guest_xpath,n,))
            acpi = {}
            default  = XMLXpath(doc, '%s[%i]/features/acpi/@default' % (guest_xpath,n,))
            toggle   = XMLXpath(doc, '%s[%i]/features/acpi/@toggle'  % (guest_xpath,n,))
            acpi['default'] = default
            acpi['toggle']  = toggle
            apic = {}
            default  = XMLXpath(doc, '%s[%i]/features/apic/@default' % (guest_xpath,n,))
            toggle   = XMLXpath(doc, '%s[%i]/features/apic/@toggle'  % (guest_xpath,n,))
            apic['default'] = default
            apic['toggle']  = toggle
            features['acpi'] = acpi
            features['apic'] = apic

            guest['os_type']  = os_type
            guest['arch']     = arch
            guest['features'] = features
            guests.append(guest)

        self.host  = host
        self.guest = guests

        return { "host" :self.host, "guest":self.guest }


    def validate(self):
        pass

if __name__ == '__main__':
    string = """<capabilities>

  <host>
    <cpu>
      <arch>x86_64</arch>
      <model>pentium3</model>
      <topology sockets='1' cores='1' threads='1'/>
      <feature name='lahf_lm'/>
      <feature name='lm'/>
      <feature name='nx'/>
      <feature name='syscall'/>
      <feature name='hypervisor'/>
      <feature name='sse4.1'/>
      <feature name='cx16'/>
      <feature name='ssse3'/>
      <feature name='pni'/>
      <feature name='ss'/>
      <feature name='sse2'/>
      <feature name='acpi'/>
      <feature name='ds'/>
      <feature name='clflush'/>
      <feature name='apic'/>
    </cpu>
    <migration_features>
      <live/>
      <uri_transports>
        <uri_transport>tcp</uri_transport>
      </uri_transports>
    </migration_features>
  </host>

  <guest>
    <os_type>hvm</os_type>
    <arch name='i686'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu</emulator>
      <machine>pc-0.12</machine>
      <machine canonical='pc-0.12'>pc</machine>
      <machine>pc-0.11</machine>
      <machine>pc-0.10</machine>
      <machine>isapc</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
    <features>
      <cpuselection/>
      <pae/>
      <nonpae/>
      <acpi default='on' toggle='yes'/>
      <apic default='on' toggle='no'/>
    </features>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='x86_64'>
      <wordsize>64</wordsize>
      <emulator>/usr/bin/qemu-system-x86_64</emulator>
      <machine>pc-0.12</machine>
      <machine canonical='pc-0.12'>pc</machine>
      <machine>pc-0.11</machine>
      <machine>pc-0.10</machine>
      <machine>isapc</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
    <features>
      <cpuselection/>
      <acpi default='on' toggle='yes'/>
      <apic default='on' toggle='no'/>
    </features>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='arm'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu-system-arm</emulator>
      <machine>integratorcp</machine>
      <machine>syborg</machine>
      <machine>musicpal</machine>
      <machine>mainstone</machine>
      <machine>n800</machine>
      <machine>n810</machine>
      <machine>cheetah</machine>
      <machine>sx1</machine>
      <machine>sx1-v1</machine>
      <machine>tosa</machine>
      <machine>akita</machine>
      <machine>spitz</machine>
      <machine>borzoi</machine>
      <machine>terrier</machine>
      <machine>connex</machine>
      <machine>verdex</machine>
      <machine>lm3s811evb</machine>
      <machine>lm3s6965evb</machine>
      <machine>realview-eb</machine>
      <machine>realview-eb-mpcore</machine>
      <machine>realview-pb-a8</machine>
      <machine>realview-pbx-a9</machine>
      <machine>versatilepb</machine>
      <machine>versatileab</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='mips'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu-system-mips</emulator>
      <machine>malta</machine>
      <machine>mipssim</machine>
      <machine>magnum</machine>
      <machine>pica61</machine>
      <machine>mips</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='mipsel'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu-system-mipsel</emulator>
      <machine>malta</machine>
      <machine>mipssim</machine>
      <machine>magnum</machine>
      <machine>pica61</machine>
      <machine>mips</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='sparc'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu-system-sparc</emulator>
      <machine>SS-5</machine>
      <machine>SS-10</machine>
      <machine>SS-600MP</machine>
      <machine>SS-20</machine>
      <machine>Voyager</machine>
      <machine>LX</machine>
      <machine>SS-4</machine>
      <machine>SPARCClassic</machine>
      <machine>SPARCbook</machine>
      <machine>SS-1000</machine>
      <machine>SS-2000</machine>
      <machine>SS-2</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
  </guest>

  <guest>
    <os_type>hvm</os_type>
    <arch name='ppc'>
      <wordsize>32</wordsize>
      <emulator>/usr/bin/qemu-system-ppc</emulator>
      <machine>g3beige</machine>
      <machine>mpc8544ds</machine>
      <machine>bamboo</machine>
      <machine>ref405ep</machine>
      <machine>taihu</machine>
      <machine>mac99</machine>
      <machine>prep</machine>
      <machine>xenpv</machine>
      <domain type='qemu'>
      </domain>
    </arch>
  </guest>

</capabilities>
"""

    param = CapabilitiesConfigParam()
    param.load_xml_config(string)

    preprint_r(param.host)
    preprint_r(param.guest) 
