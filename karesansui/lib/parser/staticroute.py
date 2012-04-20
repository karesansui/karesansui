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

import os
import re
import sys
import glob

from karesansui.lib.dict_op import DictOp
from karesansui.lib.parser.base.sh_conf_parser import shConfParser as Parser
from karesansui.lib.utils import execute_command
from karesansui.lib.utils import preprint_r
from karesansui.lib.networkaddress import NetworkAddress


"""
Define Variables for This Parser
"""
PARSER_STATICROUTE_DIR="/etc/sysconfig/network-scripts"
PARSER_STATICROUTE_FILE_PREFIX="route-"
PARSER_COMMAND_ROUTE="/sbin/route"
PARSER_COMMAND_IP="/sbin/ip"
PARSER_COMMAND_IFUP_ROUTE="/etc/sysconfig/network-scripts/ifup-routes"
PARSER_COMMAND_IFDOWN_ROUTE="/etc/sysconfig/network-scripts/ifdown-routes"
PARSER_STATICROUTE_DEFAULT_CONFIG_STYLE="old"

"""
##############
old style
##############
192.168.250.0/24 via 172.16.0.1
192.168.20.11/32 via 172.16.0.1

##############
new style
##############
GATEWAY0=172.16.0.1
NETMASK0=255.255.255.0
ADDRESS0=192.168.250.0
GATEWAY1=172.16.0.1
NETMASK1=255.255.255.255
ADDRESS1=192.168.20.11
"""


class staticrouteParser:

    _module = "staticroute"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})
        self.exclude_device_regex = "\.old|\.bak|\.rpm.*|\.20"

        self.parser = Parser()

        self.config_style = self.detect_config_style()
        if self.config_style == "old":
            self.parser.set_delim(" via ")
            self.parser.set_new_delim(" via ")
        else:
            self.parser.set_delim("=")
            self.parser.set_new_delim("=")

        self.base_parser_name = self.parser.__class__.__name__
        pass

    def detect_config_style(self):
        retval = PARSER_STATICROUTE_DEFAULT_CONFIG_STYLE

        command_args = ["grep","ADDRESS\[0\-9\]",PARSER_COMMAND_IFUP_ROUTE]
        (ret,res) = execute_command(command_args)
        if ret == 0:
            retval = "new"
            glob_str = "%s/%s" % (PARSER_STATICROUTE_DIR,PARSER_STATICROUTE_FILE_PREFIX,)
            for _afile in glob.glob("%s*" % glob_str):
                device_name =  _afile.replace(glob_str,"")
                if re.search(r"%s" % self.exclude_device_regex, device_name) is None:
                    command_args = ["grep"," via ",_afile]
                    (ret,res) = execute_command(command_args)
                    if ret == 0:
                        retval = "old"
                        break

        return retval

    def source_file(self):
        retval = []

        glob_str = "%s/%s" % (PARSER_STATICROUTE_DIR,PARSER_STATICROUTE_FILE_PREFIX,)
        for _afile in glob.glob("%s*" % glob_str):
            device_name =  _afile.replace(glob_str,"")
            if re.search(r"%s" % self.exclude_device_regex, device_name) is None:
                retval.append(_afile)

        return retval

    def convert_old_style(self, conf_arr):

        dop = DictOp()
        dop.addconf("__",{})
        orders = []
        for cnt in range(0,20):
            try:
                try:
                    exec("action  = conf_arr['ADDRESS%d']['action']" % cnt)
                except:
                    action = None

                exec("address = conf_arr['ADDRESS%d']['value']" % cnt)
                exec("netmask = conf_arr['NETMASK%d']['value']" % cnt)
                exec("gateway = conf_arr['GATEWAY%d']['value']" % cnt)

                target = "%s/%s" % (address,netmask,)
                net = NetworkAddress(target)
                try:
                    target = net.cidr
                except:
                    pass
                dop.add("__",[target],gateway)

                if action == "delete":
                    dop.delete("__",[target])

                orders.append([target])
            except:
                pass

        if len(orders) != 0:
            dop.add("__",['@ORDERS'],orders)

        return dop.getconf("__")

    def convert_new_style(self, conf_arr):

        dop = DictOp()
        dop.addconf("__",{})
        orders = []

        try:
            old_orders = conf_arr['@ORDERS']['value']
        except:
            old_orders = []

        cnt = 0
        for _k,_v in conf_arr.iteritems():

            if _k[0] != "@":
                net = NetworkAddress(_k)
                try:
                    ipaddr  = net.ipaddr
                    netmask = net.netmask
                    gateway = _v['value']
                    try:
                        action = _v['action']
                    except:
                        action = None
                    try:
                        index = old_orders.index([_k])
                    except:
                        index = cnt

                    dop.add("__",["ADDRESS%d" % index],ipaddr)
                    if action == "delete":
                        dop.delete("__",["ADDRESS%d" % index])
                    orders.insert(cnt*3+0,["ADDRESS%d" % index])

                    dop.add("__",["NETMASK%d" % index],netmask)
                    if action == "delete":
                        dop.delete("__",["NETMASK%d" % index])
                    orders.insert(cnt*3+1,["NETMASK%d" % index])

                    dop.add("__",["GATEWAY%d" % index],gateway)
                    if action == "delete":
                        dop.delete("__",["GATEWAY%d" % index])
                    orders.insert(cnt*3+2,["GATEWAY%d" % index])

                    cnt = cnt + 1
                except:
                    pass

        if len(orders) != 0:
            dop.add("__",['@ORDERS'],orders)

        return dop.getconf("__")

    def read_conf(self,extra_args=None):
        retval = {}

        for _afile in self.source_file():

            device_name = os.path.basename(_afile).replace(PARSER_STATICROUTE_FILE_PREFIX,"")
            self.parser.set_source_file([_afile])
            conf_arr = self.parser.read_conf()
            try:
                # oldスタイルの配列に統一する
                if self.config_style == "new":
                    arr = self.convert_old_style(conf_arr[_afile]['value'])
                else:
                    arr = conf_arr[_afile]['value']
 
                self.dop.set(self._module,[device_name],arr)
            except:
                pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        for device_name,_v in conf_arr.iteritems():

            _afile = "%s/%s%s" % (PARSER_STATICROUTE_DIR,PARSER_STATICROUTE_FILE_PREFIX,device_name)
            try:
                _v['action']
                if _v['action'] == "delete":
                    if os.path.exists(_afile):
                        os.unlink(_afile)
                        #pass
            except:
                continue

            try:
                _v['value']

                # newスタイルの配列に統一する
                if self.config_style == "new":
                    arr = self.convert_new_style(_v['value'])
                else:
                    arr = _v['value']

                self.dop.addconf("parser",{})
                self.dop.set("parser",[_afile],arr)
                #self.dop.preprint_r("parser")
                arr = self.dop.getconf("parser")
                self.parser.write_conf(arr,dryrun=dryrun)
            except:
                pass

        return retval

    def do_status(self):
        retval = {}

        command_args = [PARSER_COMMAND_ROUTE]
        (ret,res) = execute_command(command_args)

        ip_regex = "\d{1,3}(\.\d{1,3}){3}"
        regex = re.compile("(?P<destination>%s|default)[ \t]+(?P<gateway>%s|\*)[ \t]+(?P<netmask>%s)[ \t]+(?P<flags>[UGH]+)[ \t]+(?P<metric>\d+)[ \t]+(?P<ref>\d+)[ \t]+(?P<use>\d+)[ \t]+(?P<device>[^ ]+)" % (ip_regex,ip_regex,ip_regex,))
        for _aline in res:
            m = regex.match(_aline)
            if m:
                device      = m.group('device')
                destination = m.group('destination')
                if destination == "default":
                    destination = "0.0.0.0"
                netmask     = m.group('netmask')

                target = "%s/%s" % (destination,netmask,)
                net = NetworkAddress(target)
                target = net.cidr

                try:
                    retval[device]
                except:
                    retval[device] = {}
                retval[device][target] = {}

                for _atype in ["use","metric","ref","flags","gateway"]:
                    try:
                        exec("retval[device][target]['%s'] = m.group('%s')" % (_atype,_atype,))
                    except:
                        pass

        return retval

    def do_add(self,device,target,gateway):
        retval = True

        type = "-net"
        try:
            net = NetworkAddress(target)
            if net.netlen == 32:
                type = "-host"
            target = net.cidr
        except:
            pass
        command_args = [PARSER_COMMAND_ROUTE, "add", type, target, "gw", gateway, "dev", device]
        (ret,res) = execute_command(command_args)
        if ret != 0:
            retval = False

        return retval

    def do_del(self,device,target):
        retval = True

        type = "-net"
        try:
            net = NetworkAddress(target)
            if net.netlen == 32:
                type = "-host"
            target = net.cidr
        except:
            pass
        command_args = [PARSER_COMMAND_ROUTE, "del", type, target, "dev", device]
        (ret,res) = execute_command(command_args)
        if ret != 0:
            retval = False

        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """
    parser = staticrouteParser()

    preprint_r(parser.do_status())
    parser.do_add("eth0","5.6.7.0","172.16.0.1")
    parser.do_del("eth0","5.6.7.0")
    preprint_r(parser.do_status())

    conf_arr = parser.read_conf()
    preprint_r(conf_arr)

    dop = DictOp()
    dop.addconf("parser",conf_arr)
    dop.add("parser",["eth1","2.3.4.5/32"],"172.16.0.10")
    dop.add("parser",["eth1","2.3.4.6/32"],"172.16.0.10")
    dop.add("parser",["eth1","2.3.4.7/32"],"172.16.0.10")
    #dop.insert_order("parser",["eth1","2.3.4.5/32"],0,is_parent_parser=True)
    #dop.insert_order("parser",["eth1","2.3.4.6/32"],0,is_parent_parser=True)
    dop.insert_order("parser",["eth1","2.3.4.7/32"],1,is_parent_parser=True)
    #dop.delete("parser",["eth1","2.3.4.5/32"])
    #dop.delete("parser",["eth1","2.3.4.6/32"])
    conf_arr = dop.getconf("parser")
    preprint_r(conf_arr)
    parser.write_conf(conf_arr,dryrun=True)
