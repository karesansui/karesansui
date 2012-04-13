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
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_CHAR, CHECK_MIN, CHECK_MAX,\
     CHECK_EXIST
from karesansui.lib.utils import dict_ksort, is_param
from karesansui.lib.const import ID_MIN_LENGTH,\
     PORT_MIN_NUMBER, PORT_MAX_NUMBER

def validates_rule(obj, is_newrule=False):
    checker = Checker()
    check = True
          
    _ = obj._ 
    checker.errors = []

    obj.view.error_msg = checker.errors

    if is_newrule: 
        kit = KaresansuiIpTables()
        rule_id_max_length = 1
        if os.path.exists(kit.firewall_xml_file) is False:
            check = False
            checker.add_error(_('Has not been initialized. Please initialize.'))
        else:
            kit.firewall_xml = kit.read_firewall_xml()
            rule_id_max_length += len(kit.get_rules())

        if not is_param(obj.input, 'rule_id'):
            check = False
            checker.add_error(_('"%s" is required.') % _('ID'))
        else:
            check = checker.check_number(
                    _('ID'),
                    obj.input.rule_id,
                    CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    min = ID_MIN_LENGTH,
                    max = rule_id_max_length,
                    ) and check

    if not is_param(obj.input, 'target'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Target'))
    else:
        check = checker.check_firewall_policy(
                _('Target'),
                obj.input.target,
                CHECK_EMPTY | CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'protocol'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Protocol'))
    else:
        check = checker.check_firewall_protocol(
                _('Protocol'),
                obj.input.protocol,
                CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'source'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Source Address'))
    else:
        check = checker.check_ipaddr(
                _('Source Address'),
                obj.input.source,
                CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'sport'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Source Port'))
    else:
        if obj.input.protocol == 'tcp' or obj.input.protocol == 'udp':
            check = checker.check_number(
                    _('Source Port'),
                    obj.input.sport,
                    CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    min = PORT_MIN_NUMBER,
                    max = PORT_MAX_NUMBER,
                    ) and check

    if not is_param(obj.input, 'destination'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Destination Address'))
    else:
        check = checker.check_ipaddr(
                _('Destination Address'),
                obj.input.destination,
                CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'dport'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Destination Port'))
    else:
        if obj.input.protocol == 'tcp' or obj.input.protocol == 'udp':
            check = checker.check_number(
                    _('Destination Port'),
                    obj.input.dport,
                    CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    min = PORT_MIN_NUMBER,
                    max = PORT_MAX_NUMBER,
                    ) and check

    if not is_param(obj.input, 'inif'):
        check = False
        checker.add_error(_('"%s" is required.') % _('In Interface'))
    else:
        check = checker.check_firewall_if(
                _('In Interface'),
                obj.input.inif,
                CHECK_EXIST,
                ) and check

    if not is_param(obj.input, 'outif'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Out Interface'))
    else:
        check = checker.check_firewall_if(
                _('Out Interface'),
                obj.input.outif,
                CHECK_EXIST,
                ) and check
    
    obj.view.alert = checker.errors

    return check

class HostBy1FirewallRule(Rest):

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
            self.view.base_policy = 'ACCEPT'
            self.view.rules = kit.get_rules()
            self.view.have_config = True

        return True

urls = (
    '/host/(\d+)/firewall/rule/?(\.part)$', HostBy1FirewallRule,
    )
