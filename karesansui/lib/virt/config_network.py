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
libvirtの仮想ネットワークの設定を生成する
</comment-ja>
<comment-en>
Generate configuration file of virtual networks for libvirt.
</comment-en>

@file:   config_network.py

@author: Taizo ITO <taizo@karesansui-project.info>

@copyright:    

"""

import time
import os, stat
import re
import errno
from StringIO import StringIO
from xml.dom.minidom import DOMImplementation
implementation = DOMImplementation()

import karesansui
from karesansui.lib.const import KARESANSUI_GROUP, \
     VIRT_NETWORK_CONFIG_DIR
from karesansui.lib.utils import get_xml_parse        as XMLParse
from karesansui.lib.utils import get_xml_xpath        as XMLXpath
from karesansui.lib.utils import r_chgrp, r_chmod
from karesansui.lib.networkaddress import NetworkAddress
from karesansui.lib.file.configfile import ConfigFile

class KaresansuiNetworkConfigParamException(karesansui.KaresansuiLibException):
    pass

class NetworkConfigParam:
    def __init__(self, arg):
        if isinstance(arg, basestring):
            # expect name as string
            self.name = arg
            self.uuid = None
            self.bridge = None
            self.forward_dev = None
            self.forward_mode = None
            self.ipaddr = None
            self.netmask = None
            self.dhcp_start = None
            self.dhcp_end = None
            self.bridge_stp = None
            self.bridge_forwardDelay = None
        else:
            # expect dict in KaresansuiVirtNetwork#get_info() format
            self.name = arg['name']
            self.uuid = arg['uuid']
            self.bridge = arg['bridge']['name']
            self.forward_dev = arg['forward']['dev']
            self.forward_mode = arg['forward']['mode']
            self.ipaddr = arg['ip']['address']
            self.netmask = arg['ip']['netmask']
            self.dhcp_start = arg['dhcp']['start']
            self.dhcp_end = arg['dhcp']['end']
            try:
                self.bridge_stp = arg['bridge']['stp']
            except:
                self.bridge_stp = None
            try:
                self.bridge_forwardDelay = arg['bridge']['forwardDelay']
            except:
                self.bridge_forwardDelay = None


    def get_network_name(self):
        return self.name

    def set_uuid(self, uuid):
        self.uuid = uuid
    def get_uuid(self):
        return self.uuid

    def set_bridge(self, bridge):
        """
        @param bridge: name of the bridge
        @type bridge: string
        @return nothing
        """
        if bridge is not None:
            self.bridge = str(bridge)

    def get_bridge(self):
        return self.bridge

    def set_forward_dev(self, device):
        if device is not None:
            self.forward_dev = str(device)
    def get_forward_dev(self):
        return self.forward_dev

    def set_forward_mode(self, mode='nat'):
        if mode is not None:
            self.forward_mode = str(mode)
    def get_forward_mode(self):
        return self.forward_mode

    def set_default_networks(self, addr, dhcp_start=None, dhcp_end=None):
        self.set_netmask(NetworkAddress(addr).get('netmask'))
        self.set_ipaddr(NetworkAddress(addr).get('first_ip'))
        if not dhcp_start:
            dhcp_start = NetworkAddress(addr).get('first_ip')
        if not dhcp_end:
            dhcp_end = NetworkAddress(addr).get('last_ip')
        self.set_dhcp_start(dhcp_start)
        self.set_dhcp_end(dhcp_end)

    def get_networks(self):
        return {"ipaddr": self.ipaddr, "netmask":self.netmask,
                "dhcp_start": self.dhcp_start, "dhcp_stop":self.dhcp_stop}

    def set_ipaddr(self, addr):
        if addr is not None:
            self.ipaddr = str(addr)
    def get_ipaddr(self):
        return self.ipaddr

    def set_netmask(self, addr):
        if addr is not None:
            self.netmask = str(addr)
    def get_netmask(self):
        return self.netmask

    def set_ipaddr_and_netmask(self, addr):
        """
        Set ip address and netmask from '192.168.0.1/24' or '192.168.0.1/255.255.255.0' styled strings.
        @param addr: Strings like '192.168.0.1/24' or '192.168.0.1/255.255.255.0'.
        @type addr: string
        @return: nothing
        """
        na = NetworkAddress(addr)
        self.set_ipaddr(na.get('ipaddr'))
        self.set_netmask(na.get('netmask'))

    def set_dhcp_start(self, addr):
        if addr is not None:
            self.dhcp_start = str(addr)
    def get_dhcp_start(self):
        return self.dhcp_start

    def set_dhcp_end(self, addr):
        if addr is not None:
            self.dhcp_end = str(addr)
    def get_dhcp_end(self):
        return self.dhcp_end

    def set_bridge_stp(self, stp='on'):
        if stp is not None:
           self.bridge_stp = str(stp)
    def get_bridge_stp(self):
        return self.bridge_stp

    def set_bridge_forwardDelay(self, forwardDelay):
        if forwardDelay is not None:
            self.bridge_forwardDelay = str(forwardDelay)
    def get_bridge_forwardDelay(self):
        return self.bridge_forwardDelay

    def load_xml_config(self,path):

        if not os.path.exists(path):
            raise KaresansuiNetworkConfigParamException("no such file: %s" % path)

        document = XMLParse(path)
        uuid = XMLXpath(document,'/network/uuid/text()')
        self.set_uuid(str(uuid))

        bridge = XMLXpath(document,'/network/bridge/@name')
        self.set_bridge(bridge)

        forward_dev  = XMLXpath(document,'/network/forward/@dev')
        if forward_dev:
            self.set_forward_dev(forward_dev)
        forward_mode = XMLXpath(document,'/network/forward/@mode')
        if forward_mode:
            self.set_forward_mode(forward_mode)

        ipaddr = XMLXpath(document,'/network/ip/@address')
        self.set_ipaddr(ipaddr)

        netmask = XMLXpath(document,'/network/ip/@netmask')
        self.set_netmask(netmask)

        dhcp_start = XMLXpath(document,'/network/ip/dhcp/range/@start')
        self.set_dhcp_start(dhcp_start)

        dhcp_end = XMLXpath(document,'/network/ip/dhcp/range/@end')
        self.set_dhcp_end(dhcp_end)

        bridge_stp = XMLXpath(document,'/network/bridge/@stp')
        self.set_bridge_stp(bridge_stp)

        bridge_forwardDelay = XMLXpath(document,'/network/bridge/@forwardDelay')
        self.set_bridge_forwardDelay(bridge_forwardDelay)

    def validate(self):

        if not self.uuid:
            raise KaresansuiNetworkConfigParamException("ConfigParam: uuid is None")
        if not self.name or not len(self.name):
            raise KaresansuiNetworkConfigParamException("ConfigParam: illegal name")

class NetworkXMLGenerator:

    def _create_text_node(self, tag, txt):
        node = self.document.createElement(tag)
        self._add_text(node, txt)
        return node

    def _add_text(self, node, txt):
        txt_n = self.document.createTextNode(txt)
        node.appendChild(txt_n)

    def generate(self, config):
        tree = self.generate_xml_tree(config)
        out = StringIO()
        out.write(tree.toxml())
        return out.getvalue()

class NetworkXMLConfigGenerator(NetworkXMLGenerator):

    def __init__(self):
        self.config_dir = VIRT_NETWORK_CONFIG_DIR

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config

        self.begin_build()
        self.build_bridge()
        self.build_forward()
        self.build_ip()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.network = self.document.createElement("network")

        name = self._create_text_node("name", self.config.get_network_name())
        uuid = self._create_text_node("uuid", self.config.get_uuid())
        self.network.appendChild(name)
        self.network.appendChild(uuid)

        self.document.appendChild(self.network)

    def build_bridge(self):
        doc = self.document
        if self.config.get_bridge():
            bridge = doc.createElement("bridge")
            bridge.setAttribute("name", self.config.get_bridge())

            if self.config.get_bridge_stp() is not None:
                bridge.setAttribute("stp", self.config.get_bridge_stp())
            else:
                bridge.setAttribute("stp", "on")

            if self.config.get_bridge_forwardDelay() is not None:
                bridge.setAttribute("forwardDelay", self.config.get_bridge_forwardDelay())
            else:
                bridge.setAttribute("forwardDelay", "0")

            self.network.appendChild(bridge)

    def build_forward(self):
        doc = self.document
        if self.config.get_forward_dev() is not None or \
           self.config.get_forward_mode() is not None:

            forward = doc.createElement("forward")
            if self.config.get_forward_dev() is not None:
                forward.setAttribute("dev", self.config.get_forward_dev())
            if self.config.get_forward_mode() is not None:
                forward.setAttribute("mode", self.config.get_forward_mode())
            self.network.appendChild(forward)

    def build_ip(self):
        doc = self.document
        ip = doc.createElement("ip")
        ip.setAttribute("netmask", self.config.get_netmask())
        ip.setAttribute("address", self.config.get_ipaddr())
        self.network.appendChild(ip)

        dhcp = doc.createElement("dhcp")
        range = doc.createElement("range")
        range.setAttribute("start", self.config.get_dhcp_start())
        range.setAttribute("end", self.config.get_dhcp_end())
        dhcp.appendChild(range)
        ip.appendChild(dhcp)

    def end_build(self):
        pass

    def writecfg(self,cfg):
        try:
            os.makedirs(self.config_dir)
        except OSError, (err, msg):
            if err != errno.EEXIST:
                raise OSError(err,msg)

        filename = "%s/%s.xml" %(self.config_dir,self.config.get_network_name())
        ConfigFile(filename).write(cfg)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

