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

import time
import re

import web

from karesansui.gadget.hostby1firewallrule import validates_rule
from karesansui.lib.rest import Rest, auth
from karesansui.lib.firewall.iptables import KaresansuiIpTables
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_CHAR, \
     CHECK_MIN, CHECK_MAX
from karesansui.lib.const import \
     ID_MIN_LENGTH, ID_MAX_LENGTH


from karesansui.lib.utils import get_ifconfig_info

def validates_param_id(obj, rule_id):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    check = checker.check_number(
            _('Firewall Rule ID'),
            rule_id,
            CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
            min = ID_MIN_LENGTH,
            max = ID_MAX_LENGTH,
        ) and check

    obj.view.alert = checker.errors

    return check
     
class HostBy1FirewallRuleby1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        rule_id = param[1]
        if not validates_param_id(self, rule_id):
            return web.notfound(self.view.alert)

        kit = KaresansuiIpTables()
        kit.firewall_xml = kit.read_firewall_xml()

        rules = kit.get_rules()
        cnt = 1
        for rule in rules:
            if cnt == int(rule_id):
                self.view.rule = rule
                break
            cnt = cnt + 1

        if self.is_mode_input():
            self.view.targets = kit.basic_targets['filter']
            self.view.protocols = kit.chain_protos
            self.view.netinfo = get_ifconfig_info()
            devtype_regexs = {
                "phy":"^(lo|eth)",
                "vir":"^(xenbr|virbr|vif|veth)",
                }
            devtype_phy_regex = re.compile(r"%s" % devtype_regexs['phy'])
            devtype_vir_regex = re.compile(r"%s" % devtype_regexs['vir'])

            devs = {}
            devs['phy'] = []
            devs['vir'] = []
            devs['oth'] = []
            cidrs = []
            ips = []
            for dev,dev_info in get_ifconfig_info().iteritems():
                try:
                    if devtype_phy_regex.match(dev):
                        devs['phy'].append(dev)
                    elif devtype_vir_regex.match(dev):
                        devs['vir'].append(dev)
                    else:
                        devs['oth'].append(dev)
                    if dev_info['ipaddr'] is not None:
                        if not dev_info['ipaddr'] in ips:
                            ips.append(dev_info['ipaddr'])
                    if dev_info['cidr'] is not None:
                        if not dev_info['cidr'] in cidrs:
                            cidrs.append(dev_info['cidr'])
                except:
                    pass
            devs['phy'].sort()
            devs['vir'].sort()
            devs['oth'].sort()
            self.view.devs = [{'Physical' : devs['phy']},
                              {'Virtual' : devs['vir']},
                              {'Other' : devs['oth']},
                              ]
            self.view.cidrs = cidrs
            self.view.ips = ips
            return True
        else:
            return web.nomethod()

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()
        
        if not validates_rule(self):
            return web.badrequest(self.view.alert)

        rule_id = int(param[1])
        if not validates_param_id(self, rule_id):
            return web.notfound(self.view.alert)


        self.view.host_id = host_id

        kit = KaresansuiIpTables()
        kit.firewall_xml = kit.read_firewall_xml()

        rule_info = {"target" : self.input.target,
                     "protocol" : self.input.protocol,
                     "source" : self.input.source,
                     "destination" : self.input.destination,
                     "source-port" : self.input.sport,
                     "destination-port" : self.input.dport,
                     "in-interface" : self.input.inif,
                     "out-interface" : self.input.outif,
                     }
        rule_id = kit.modify_rule(rule_id,rule_info)
        kit.write_firewall_xml()
        
        return web.seeother("%s?mode=input" % web.ctx.path)


    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        rule_id = param[1]
        if not validates_param_id(self, rule_id):
            return web.notfound(self.view.alert)


        new_rules = []

        kit = KaresansuiIpTables()
        kit.firewall_xml = kit.read_firewall_xml()
        kit.delete_rule(int(rule_id))
        kit.write_firewall_xml()
        return web.seeother("%s.part" % web.ctx.path[:web.ctx.path.rfind('/')])

urls = (
    '/host/(\d+)/firewall/rule/(\d+)/?(\.part)$', HostBy1FirewallRuleby1,
    )
