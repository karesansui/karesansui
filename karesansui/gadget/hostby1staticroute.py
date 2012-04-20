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

import web
import simplejson as json

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.db.access.machine import findbyhost1

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_CHAR, CHECK_MIN, CHECK_MAX, CHECK_ONLYSPACE, \
    CHECK_UNIQUE

from karesansui.lib.utils import is_param, is_empty, preprint_r, \
    base64_encode, get_ifconfig_info

from karesansui.lib.networkaddress import NetworkAddress
from karesansui.lib.parser.staticroute import staticrouteParser as Parser
from karesansui.lib.conf import read_conf, write_conf

def validates_staticroute(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'target'):
        check = False
        checker.add_error(_('Specify target address for the route.'))
    else:
        check = checker.check_ipaddr(
                _('Target'), 
                obj.input.target,
                CHECK_EMPTY | CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'gateway'):
        check = False
        checker.add_error(_('Specify gateway address for the route.'))
    else:
        check = checker.check_ipaddr(
                _('Gateway'), 
                obj.input.gateway,
                CHECK_VALID,
                ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1StaticRoute(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        host = findbyhost1(self.orm, host_id)

        self.view.host_id = host_id

        # unremovable entries
        excludes = {
                   "device": ["^peth","^virbr","^sit","^xenbr","^lo","^br"],
                   "ipaddr": ["^0\.0\.0\.0$", "^169\.254\.0\.0$"],
                   }

        devices = []
        phydev_regex = re.compile(r"^eth[0-9]+")
        for dev,dev_info in get_ifconfig_info().iteritems():
            if phydev_regex.match(dev):
                try:
                    if dev_info['ipaddr'] is not None:
                        devices.append(dev)
                        net = NetworkAddress("%s/%s" % (dev_info['ipaddr'],dev_info['mask'],))
                        excludes['ipaddr'].append(net.network)
                except:
                    pass

        self.view.devices = devices

        parser = Parser()
        status = parser.do_status()
        routes = {}
        for _k,_v in status.iteritems():
            for _k2,_v2 in _v.iteritems():
                name = base64_encode("%s@%s" % (_k2,_k,))
                routes[name] = {}
                routes[name]['name']    = name
                routes[name]['device']  = _k
                routes[name]['gateway'] = _v2['gateway']
                routes[name]['flags']   = _v2['flags']
                routes[name]['ref']     = _v2['ref']
                routes[name]['use']     = _v2['use']
                net = NetworkAddress(_k2)
                routes[name]['ipaddr']  = net.ipaddr
                routes[name]['netlen']  = net.netlen
                routes[name]['netmask'] = net.netmask

                removable = True
                for _ex_key,_ex_val in excludes.iteritems():
                    ex_regex = "|".join(_ex_val)
                    mm = re.search(ex_regex,routes[name][_ex_key])
                    if mm:
                        removable = False

                routes[name]['removable'] = removable

        self.view.routes = routes

        if self.is_mode_input():
            pass

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        host = findbyhost1(self.orm, host_id)

        if not validates_staticroute(self):
            return web.badrequest(self.view.alert)

        modules = ["staticroute"]

        dop = read_conf(modules, self, host)
        if dop is False:
            return web.internalerror('Internal Server Error. (Timeout)')

        target  = self.input.target
        net = NetworkAddress(target)
        ipaddr  = net.ipaddr
        netmask = net.netmask
        netlen  = net.netlen
        network = net.network
        target = "%s/%s" % (ipaddr,netlen,)
        gateway = self.input.gateway
        device  = self.input.device

        dop.set("staticroute", [device,target], gateway)

        from karesansui.lib.parser.staticroute import PARSER_COMMAND_ROUTE
        if net.netlen == 32:
            command = "%s add -host %s gw %s dev %s" % (PARSER_COMMAND_ROUTE,ipaddr,gateway,device,)
            command = "%s add -host %s dev %s" % (PARSER_COMMAND_ROUTE,ipaddr,device,)
        else:
            command = "%s add -net %s netmask %s gw %s dev %s" % (PARSER_COMMAND_ROUTE,network,netmask,gateway,device,)
        extra_args = {"post-command": command}

        retval = write_conf(dop, self, host, extra_args=extra_args)
        if retval is False:
            return web.internalerror('Internal Server Error. (Adding Task)')

        return web.accepted(url=web.ctx.path)

urls = (
    '/host/(\d+)/staticroute[/]?(\.html|\.part|\.json)?$', HostBy1StaticRoute,
    )

