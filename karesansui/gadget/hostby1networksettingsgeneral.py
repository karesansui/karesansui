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
import sys
import re
import time
import web

from karesansui.lib.rest import Rest, auth

from karesansui.db.access.machine import findbyhost1
from karesansui.lib.utils import get_ifconfig_info, dict_ksort, is_param
from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.const import FQDN_MIN_LENGTH, \
    FQDN_MAX_LENGTH

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH

def validates_general(obj):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'gateway'):
        check = checker.check_ipaddr(_('Default Gateway'),
                                     obj.input.gateway,
                                     CHECK_EMPTY | CHECK_VALID,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Default Gateway'))

    if is_param(obj.input, 'fqdn'):
        check = checker.check_domainname(_('FQDN'),
                                         obj.input.fqdn,
                                         CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                                         FQDN_MIN_LENGTH,
                                         FQDN_MAX_LENGTH,
                                         ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('FQDN'))

    if is_param(obj.input, 'nameserver'):
        nameservers = obj.input.nameserver.strip().split()
        if len(nameservers) != 0:
            for name_server in nameservers:
                if name_server == "":
                    continue
                check = checker.check_ipaddr(_('Nameserver'),
                                             name_server,
                                             CHECK_VALID,
                                             ) and check
        else:
            check = False
            checker.add_error(_('"%s" is required.') %_('Nameserver'))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Nameserver'))

    obj.view.alert = checker.errors
    return check

class HostBy1NetworkSettingsGeneral(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        self.view.current = get_ifconfig_info()

        modules = ["network","resolv","hosts"]

        host = findbyhost1(self.orm, host_id)
        dop = read_conf(modules, self, host)
        if dop is False:
            return web.internalerror('Internal Server Error. (Timeout)')

        self.view.gateway    = dop.get("network",["GATEWAY"])
        self.view.search     = dop.get("resolv" ,["search"])

        self.view.nameserver = dop.get("resolv" ,["nameserver"])
        if self.view.nameserver is False:
            self.view.nameserver = []
        if type(self.view.nameserver) == str:
            self.view.nameserver = [self.view.nameserver]
        self.view.nameserver = "\n".join(self.view.nameserver)

        self.view.domainname  = dop.get("resolv" ,["domain"])
        if self.view.domainname is False:
            self.view.domainname = dop.get("network" ,["DOMAINNAME"])
        if self.view.domainname is False:
            self.view.domainname = re.sub("^[^\.]+\.","",os.uname()[1])

        self.view.hostname = dop.get("network" ,["HOSTNAME"])
        if self.view.hostname is False:
            self.view.hostname = os.uname()[1]

        self.view.hostname_short = re.sub("\.%s$" % (self.view.domainname), "", self.view.hostname)

        # --
        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_general(self):
            self.logger.debug("Change network general failed. Did not validate.")
            return web.badrequest(self.view.alert)

        modules = ["network","resolv","hosts"]

        host = findbyhost1(self.orm, host_id)
        dop = read_conf(modules, self, host)
        if dop is False:
            self.logger.error("Change network general failed. Failed read conf.")
            return web.internalerror('Internal Server Error. (Read Conf)')

        gateway  = self.input.gateway
        hostname = self.input.fqdn
        nameservers = self.input.nameserver.strip().split()

        domainname     = re.sub("^[^\.]+\.","",hostname)
        hostname_short = re.sub("\.%s$" % (domainname), "", hostname)

        old_domainname  = dop.get("resolv" ,["domain"])
        if old_domainname is False:
            old_domainname = dop.get("network" ,["DOMAINNAME"])
        if old_domainname is False:
            old_domainname = re.sub("^[^\.]+\.","",os.uname()[1])

        old_hostname = dop.get("network" ,["HOSTNAME"])
        if old_hostname is False:
            old_hostname = os.uname()[1]

        old_hostname_short = re.sub("\.%s$" % (old_domainname), "", old_hostname)

        # hosts
        hosts_arr = dop.getconf("hosts")
        for _k,_v in hosts_arr.iteritems():
            _host = dop.get("hosts",[_k])
            _value   = _host[0]
            _comment = _host[1]
            _values  = _value.strip().split()
            new_values = []
            for _entry in _values:
                if _entry == old_hostname:
                    _entry = hostname
                elif _entry == old_hostname_short:
                    _entry = hostname_short
                new_values.append(_entry)
            new_value = " ".join(new_values)
            dop.set("hosts" ,[_k] ,[new_value,_comment])

        dop.set("network" ,["GATEWAY"]    ,gateway)
        dop.set("resolv"  ,["nameserver"] ,nameservers)
        dop.set("resolv"  ,["domain"]     ,domainname)
        dop.set("network" ,["DOMAINNAME"] ,domainname)
        dop.set("network" ,["HOSTNAME"]   ,hostname)

        retval = write_conf(dop, self, host)
        if retval is False:
            self.logger.error("Change network general failed. Failed write conf.")
            return web.internalerror('Internal Server Error. (Write Conf)')

        return web.accepted(url=web.ctx.path)

urls = (
    '/host/(\d+)/networksettings/general/?(\.part)?$', HostBy1NetworkSettingsGeneral,
    )
