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

import web
import simplejson as json

#import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.db.access.machine import findbyhost1

from karesansui.lib.utils import preprint_r, base64_encode, base64_decode

from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.parser.staticroute import staticrouteParser as Parser
from karesansui.lib.networkaddress import NetworkAddress

from karesansui.gadget.hostby1staticroute import validates_staticroute

from karesansui.lib.checker import *

class HostBy1StaticRouteBy1(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        b64name = param[1]
        if not (b64name and host_id):
            return web.badrequest()

        name = base64_decode(str(b64name))

        (target, device) = name.split("@")

        net = NetworkAddress(target)
        ipaddr  = net.ipaddr
        netmask = net.netmask
        netlen  = net.netlen

        gateway = _('N/A')
        flags   = _('N/A')
        ref     = _('N/A')
        use     = _('N/A')
        metric  = _('N/A')

        parser = Parser()
        status = parser.do_status()
        for _k,_v in status.iteritems():
            for _k2,_v2 in _v.iteritems():
                if name == "%s@%s" % (_k2,_k,):
                    gateway = _v2['gateway']
                    flags   = _v2['flags']
                    ref     = _v2['ref']
                    use     = _v2['use']
                    metric  = _v2['metric']

        route = dict(name=name,
                       ipaddr=ipaddr,
                       netmask=netmask,
                       netlen=netlen,
                       device=device,
                       gateway=gateway,
                       flags=flags,
                       ref=ref,
                       use=use,
                       metric=metric,
                       )

        self.view.route = route
        return True

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()
        
        b64name = param[1]
        if not (b64name and host_id):
            return web.badrequest()

        host = findbyhost1(self.orm, host_id)

        name = base64_decode(str(b64name))

        (target, device) = name.split("@")

        net = NetworkAddress(target)
        ipaddr  = net.ipaddr
        netmask = net.netmask
        netlen  = net.netlen
        target = "%s/%s" % (ipaddr,netlen,)

        modules = ["staticroute"]

        dop = read_conf(modules, self, host)
        if dop is False:
            return web.internalerror('Internal Server Error. (Timeout)')

        dop.delete("staticroute", [device,target])

        from karesansui.lib.parser.staticroute import PARSER_COMMAND_ROUTE
        if net.netlen == 32:
            command = "%s del -host %s dev %s" % (PARSER_COMMAND_ROUTE,ipaddr,device,)
        else:
            command = "%s del -net %s netmask %s dev %s" % (PARSER_COMMAND_ROUTE,ipaddr,netmask,device,)
        extra_args = {"post-command": command}

        retval = write_conf(dop, self, host, extra_args=extra_args)
        if retval is False:
            return web.internalerror('Internal Server Error. (Adding Task)')

        return web.accepted()

urls = (
    '/host/(\d+)/staticroute/([a-zA-Z0-9\=]{2,})/?(\.html|\.part|\.json)?$', HostBy1StaticRouteBy1,

    )

