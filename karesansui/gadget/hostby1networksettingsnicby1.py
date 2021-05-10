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
import web

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.db.model._2pysilhouette import Job, JobGroup
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from pysilhouette.command import dict2command

from karesansui.lib.utils import get_ifconfig_info, dict_ksort, get_bonding_info, is_param
from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.networkaddress import NetworkAddress
from karesansui.lib.const import BONDING_COMMAND_DELETE

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID

def validates_nic(obj):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'bootproto'):
        if obj.input.bootproto == "static":
            if is_param(obj.input, 'ipaddr'):
                check = checker.check_ipaddr(_('IP Address'),
                                             obj.input.ipaddr,
                                             CHECK_EMPTY | CHECK_VALID,
                                             ) and check
            else:
                check = False
                checker.add_error(_('"%s" is required.') %_('IP Address'))

            if is_param(obj.input, 'netmask'):
                check = checker.check_netmask(_('Netmask'),
                                              obj.input.netmask,
                                              CHECK_EMPTY | CHECK_VALID,
                                              ) and check
            else:
                check = False
                checker.add_error(_('"%s" is required.') %_('Netmask'))

        else:
            if is_param(obj.input, 'ipaddr'):
                check = checker.check_ipaddr(_('IP Address'),
                                             obj.input.ipaddr,
                                             CHECK_VALID,
                                             ) and check

            if is_param(obj.input, 'netmask'):
                check = checker.check_netmask(_('Netmask'),
                                              obj.input.netmask,
                                              CHECK_VALID,
                                              ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Boot-time Protocol'))

    obj.view.alert = checker.errors
    return check

class HostBy1NetworkSettingsNicBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        self.view.current = get_ifconfig_info()
        self.view.device = param[1]

        modules = ["ifcfg"]

        host = findbyhost1(self.orm, host_id)
        dop = read_conf(modules,self,host)
        if dop is False:
            self.logger.error("Get nic info failed. Failed read conf.")
            return web.internalerror('Internal Server Error. (Read conf)')

        self.view.bootproto = dop.get("ifcfg",[self.view.device,"BOOTPROTO"])
        if self.view.bootproto is False:
            self.view.bootproto = "static"

        self.view.onboot    = dop.get("ifcfg",[self.view.device,"ONBOOT"])
        if self.view.onboot is False:
            self.view.onboot = "yes"

        self.view.ipaddr    = dop.get("ifcfg",[self.view.device,"IPADDR"])
        if self.view.ipaddr is False:
            self.view.ipaddr = ""

        self.view.netmask   = dop.get("ifcfg",[self.view.device,"NETMASK"])
        if self.view.netmask is False:
            self.view.netmask = ""

        self.view.network   = dop.get("ifcfg",[self.view.device,"NETWORK"])
        if self.view.network is False:
            net = NetworkAddress("%s/%s" % (self.view.ipaddr,self.view.netmask))
            if net.valid_addr(self.view.ipaddr) is True and net.valid_addr(self.view.netmask) is True:
                self.view.network = net.network
            else:
                self.view.network = ""

        self.view.broadcast = dop.get("ifcfg",[self.view.device,"BROADCAST"])
        if self.view.broadcast is False:
            net = NetworkAddress("%s/%s" % (self.view.ipaddr,self.view.netmask))
            if net.valid_addr(self.view.ipaddr) is True and net.valid_addr(self.view.netmask) is True:
                self.view.broadcast = net.broadcast
            else:
                self.view.broadcast = ""

        self.view.master    = dop.get("ifcfg",[self.view.device,"MASTER"])
        if self.view.master is False:
            self.view.master = ""

        self.view.c_ipaddr    = self.view.current[self.view.device]["ipaddr"]
        if self.view.c_ipaddr is None:
            self.view.c_ipaddr = ""

        self.view.c_netmask   = self.view.current[self.view.device]["mask"]
        if self.view.c_netmask is None:
            self.view.c_netmask = ""

        if self.view.current[self.view.device]["cidr"] is None:
            self.view.c_network = ""
        else:
            self.view.c_network = re.sub("\/.*","",self.view.current[self.view.device]["cidr"])

        self.view.c_broadcast = self.view.current[self.view.device]["bcast"]
        if self.view.c_broadcast is None:
            net = NetworkAddress("%s/%s" % (self.view.c_ipaddr,self.view.c_netmask))
            if net.valid_addr(self.view.c_ipaddr) is True and net.valid_addr(self.view.c_netmask) is True:
                self.view.c_broadcast = net.broadcast
            else:
                self.view.c_broadcast = ""

        self.view.c_hwaddr = self.view.current[self.view.device]["hwaddr"]
        if self.view.c_hwaddr is None:
            self.view.c_hwaddr = ""

        self.view.bond_info = get_bonding_info()

        self.view.c_master = ""
        for bond in self.view.bond_info:
            for slave in self.view.bond_info[bond]['slave']:
                if self.view.device == slave:
                    self.view.c_master = bond

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        uni_device = param[1]
        if uni_device is None: return web.notfound()
        device = uni_device.encode("utf-8")

        if not validates_nic(self):
            self.logger.debug("Change nic failed. Did not validate.")
            return web.badrequest(self.view.alert)

        host = findbyhost1(self.orm, host_id)

        modules = ["ifcfg"]
        dop = read_conf(modules, self, host)
        if dop is False:
            self.logger.error("Change nic failed. Failed read conf.")
            return web.internalerror('Internal Server Error. (Read conf)')

        ipaddr = ""
        if is_param(self.input, ipaddr):
            if self.input.ipaddr:
                ipaddr = self.input.ipaddr

        netmask = ""
        if is_param(self.input, netmask):
            if self.input.netmask:
                netmask = self.input.netmask

        bootproto = self.input.bootproto
        onboot = "no"
        if is_param(self.input, 'onboot'):
            onboot = "yes"

        net = NetworkAddress("%s/%s" % (ipaddr,netmask))
        network   = net.network
        broadcast = net.broadcast

        if not dop.get("ifcfg", device):
            self.logger.error("Change nic failed. Target config not found.")
            return web.internalerror('Internal Server Error. (Get conf)')

        dop.set("ifcfg",[device,"ONBOOT"]   ,onboot)
        dop.set("ifcfg",[device,"BOOTPROTO"],bootproto)
        dop.set("ifcfg",[device,"IPADDR"]   ,ipaddr)
        dop.set("ifcfg",[device,"NETMASK"]  ,netmask)
        if network is not None:
            dop.set("ifcfg",[device,"NETWORK"]  ,network)
        if broadcast is not None:
            dop.set("ifcfg",[device,"BROADCAST"],broadcast)

        retval = write_conf(dop, self, host)
        if retval is False:
            self.logger.error("Change nic failed. Failed write conf.")
            return web.internalerror('Internal Server Error. (Adding Task)')

        return web.accepted(url=web.ctx.path)

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        device = param[1]
        if device is None: return web.notfound()

        cmdname = "Delete Bonding Setting"
        cmd = BONDING_COMMAND_DELETE
        options = {}

        options['dev'] = device
        options["succession"] = None

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _job = Job('%s command' % cmdname, 0, _cmd)
        _jobgroup.jobs.append(_job)

        host = findbyhost1(self.orm, host_id)
        _machine2jobgroup = m2j_new(machine=host,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )

        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               _jobgroup,
                               )
        return web.accepted()

urls = (
    '/host/(\d+)/networksettings/nic/([^\./]+)/?(\.part|\.json)?$', HostBy1NetworkSettingsNicBy1,
    )
