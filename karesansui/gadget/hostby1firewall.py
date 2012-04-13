# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
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
import os

import web
from web.utils import Storage

from karesansui.lib.rest import Rest, auth
from karesansui.lib.firewall.iptables import KaresansuiIpTables
from karesansui.gadget.hostby1firewallrule import validates_rule
from karesansui.lib.utils import get_ifconfig_info, dict_ksort

class HostBy1Firewall(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        
        kit = KaresansuiIpTables()
        
        if os.path.exists(kit.firewall_xml_file) is False:
            self.view.have_config = False
        else:
            kit.firewall_xml = kit.read_firewall_xml()
            # --
            self.view.iptables = Storage(
                is_running=kit.is_running(),
                is_configured=kit.is_configured(),
                )
            self.view.have_config = True

            if self.is_mode_input() is True:

                self.view.default_rule_id = len(kit.get_rules()) + 1
                self.view.targets = kit.basic_targets['filter']
                self.view.protocols = kit.chain_protos
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

        # --
        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_rule(self, is_newrule=True):
            return web.badrequest(self.view.alert)
        
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

        if self.input.rule_id == "":
            rule_id = kit.add_rule(rule_info)
        else:
            rule_id = kit.insert_rule(int(self.input.rule_id),rule_info)

        kit.write_firewall_xml()
        
        self.view.host_id = host_id
        
        return web.created('%s/%d' % (web.ctx.path, rule_id,))


urls = (
    '/host/(\d+)/firewall/?(\.part)$', HostBy1Firewall,
    )
