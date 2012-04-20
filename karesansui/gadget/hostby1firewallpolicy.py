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
import time

import web
from web.utils import Storage

from karesansui.lib.rest import Rest, auth
from karesansui.lib.firewall.iptables import KaresansuiIpTables
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_CHAR
from karesansui.lib.utils import is_param

def validates_policy(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'input_policy'):
        check = False
        checker.add_error(_('"%s" is required.') % _('INPUT Chain'))
    else:
        check = checker.check_firewall_policy(
                _('INPUT Chain'),
                obj.input.input_policy,
                CHECK_EMPTY | CHECK_VALID
                ) and check

    if not is_param(obj.input, 'output_policy'):
        check = False
        checker.add_error(_('"%s" is required.') % _('OUTPUT Chain'))
    else:
        check = checker.check_firewall_policy(
                _('OUTPUT Chain'),
                obj.input.output_policy,
                CHECK_EMPTY | CHECK_VALID
                ) and check

    if not is_param(obj.input, 'forward_policy'):
        check = False
        checker.add_error(_('"%s" is required.') % _('FORWARD Chain'))
    else:
        check = checker.check_firewall_policy(
                _('FORWARD Chain'),
                obj.input.input_policy,
                CHECK_EMPTY | CHECK_VALID
                ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1FirewallPolicy(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()
        
        self.view.host_id = host_id

        kit = KaresansuiIpTables()

        if os.path.exists(kit.firewall_xml_file) is False:
            self.view.have_config = False
        else:
            self.view.have_config = True
            kit.firewall_xml = kit.read_firewall_xml()

            for chain in kit.basic_chains['filter']:
                try:
                    policy = kit.firewall_xml['filter'][chain]['policy']
                except:
                    policy = 'ACCEPT'
                chain = chain.lower()
                exec("self.view.%s_policy_ACCEPT_checked = ''" % chain)
                exec("self.view.%s_policy_DROP_checked = ''" % chain)
                exec("self.view.%s_policy_REJECT_checked = ''" % chain)
                if policy == 'REJECT':
                    exec("self.view.%s_policy = 'REJECT'" % chain)
                    exec("self.view.%s_policy_REJECT_checked = 'checked'" % chain)
                elif policy == 'DROP':
                    exec("self.view.%s_policy = 'DROP'" % chain)
                    exec("self.view.%s_policy_DROP_checked = 'checked'" % chain)
                    self.view.base_policy_DROP_checked = 'checked';
                else:
                    exec("self.view.%s_policy = 'ACCEPT'" % chain)
                    exec("self.view.%s_policy_ACCEPT_checked = 'checked'" % chain)

            self.view.iptables = Storage(
                is_running=kit.is_running(),
                is_configured=kit.is_configured(),
            )

            self.view.targets = kit.basic_targets['filter']

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        kit = KaresansuiIpTables()
        kit.firewall_xml = kit.read_firewall_xml()
        
        if not validates_policy(self):
            self.logger.debug("Create account is failed, Invalid input value")
            return web.badrequest(self.view.alert)
        
        kit.modify_policy("INPUT",  self.input.input_policy)
        kit.modify_policy("OUTPUT", self.input.output_policy)
        kit.modify_policy("FORWARD",self.input.forward_policy)
        kit.write_firewall_xml()

        for chain in kit.basic_chains['filter']:
            try:
                policy = kit.firewall_xml['filter'][chain]['policy']
            except:
                policy = 'ACCEPT'
            chain = chain.lower()
            exec("self.view.%s_policy_ACCEPT_checked = ''" % chain)
            exec("self.view.%s_policy_DROP_checked = ''" % chain)
            exec("self.view.%s_policy_REJECT_checked = ''" % chain)
            if policy == 'REJECT':
                exec("self.view.%s_policy = 'REJECT'" % chain)
                exec("self.view.%s_policy_REJECT_checked = 'checked'" % chain)
            elif policy == 'DROP':
                exec("self.view.%s_policy = 'DROP'" % chain)
                exec("self.view.%s_policy_DROP_checked = 'checked'" % chain)
                self.view.base_policy_DROP_checked = 'checked';
            else:
                exec("self.view.%s_policy = 'ACCEPT'" % chain)
                exec("self.view.%s_policy_ACCEPT_checked = 'checked'" % chain)

        return web.seeother(web.ctx.path)

urls = ('/host/(\d+)/firewall/policy/?(\.part)$', HostBy1FirewallPolicy,)
