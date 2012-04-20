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

from karesansui.lib.utils import get_ifconfig_info, get_bonding_info, dict_ksort, available_virt_mechs, is_param
from karesansui.lib.const import BONDING_COMMAND_ADD, NETWORK_COMMAND_RESTART, BONDING_MODE

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID

NETWORK_RESTART = 1

def validates_bonding(obj, target_regex):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    count = 0
    for input in obj.input:
        m = target_regex.match(input)
        if m:
            count += 1
            check = checker.check_netdev_name(_('Target Device Name'),
                                              m.group('dev'),
                                              CHECK_EMPTY | CHECK_VALID,
                                              ) and check
    if count < 2:
        check = False
        checker.add_error(_('Not enough target devices for bonding.'))

    if is_param(obj.input, 'bonding_target_dev_primary'):
        check = checker.check_netdev_name(_('Primary Device Name'),
                                          obj.input.bonding_target_dev_primary,
                                          CHECK_EMPTY | CHECK_VALID,
                                          ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Primary Device Name'))

    if is_param(obj.input, 'bonding_mode'):
        if obj.input.bonding_mode not in BONDING_MODE:
            check = False
            checker.add_error(_('Unknown bonding mode.'))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Bonding Mode'))

    obj.view.alert = checker.errors
    return check

class HostBy1NetworkSettings(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        bond_list = get_bonding_info()

        if self.is_mode_input() is True:
            exist_bond_max_num = -1
            exist_bond_list = get_ifconfig_info("regex:^bond")
            for bond_name in exist_bond_list.keys():
                try:
                    num = int(bond_name.replace("bond",""))
                except ValueError:
                    continue

                if exist_bond_max_num < num:
                    exist_bond_max_num = num

            self.view.create_bond_name = "bond%s" % (exist_bond_max_num + 1)
            dev_list = get_ifconfig_info("regex:^eth")
            for bond in bond_list:
                for slave in bond_list[bond]['slave']:
                    if slave in dev_list:
                        dev_list[slave]['bond'] = bond

            #pysical_dev_list = get_ifconfig_info("regex:^peth")
            pysical_dev_list = get_ifconfig_info("regex:^br")
            for pysical_dev in pysical_dev_list:
                if pysical_dev[1:] in dev_list:
                    dev_list[pysical_dev[1:]]['bridge'] = pysical_dev

            self.view.bond_target_dev = dev_list
            self.view.hypervisors = available_virt_mechs()
            return True

        dev_list = get_ifconfig_info()

        for bond in bond_list:
            if bond in dev_list:
                dev_list[bond]['bond'] = True
                for slave in bond_list[bond]['slave']:
                    for dev in dev_list:
                        if dev == slave:
                            dev_list[dev]['bond'] = True

        self.view.current = dev_list
        self.view.bond_list = bond_list

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        target_regex = re.compile(r"^bonding_target_dev_select_(?P<dev>eth[0-9]+)")

        if not validates_bonding(self, target_regex):
            self.logger.debug("Add bonding failed. Did not validate.")
            return web.badrequest(self.view.alert)

        target_dev = []
        for input in self.input:
            m = target_regex.match(input)
            if m:
                target_dev.append(m.group('dev'))

        primary = self.input.bonding_target_dev_primary
        mode    = self.input.bonding_mode

        cmdname = u"Add Bonding Setting"
        cmd = BONDING_COMMAND_ADD
        options = {}

        options['dev'] = ','.join(target_dev)
        options["primary"] = primary
        options["mode"] = mode

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

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id

        host = findbyhost1(self.orm, host_id)

        status = int(self.input.status)
        if status != NETWORK_RESTART:
            return web.badrequest()

        cmdname = u"Restart Network"
        cmd = NETWORK_COMMAND_RESTART
        options = {}

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
    '/host/(\d+)/networksettings/?(\.part)$', HostBy1NetworkSettings,
    )
