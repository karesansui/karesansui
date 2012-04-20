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

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import VIRT_COMMAND_CREATE_NETWORK
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import jobgroup_findbyuniqkey
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from pysilhouette.command import dict2command
from karesansui.db.model._2pysilhouette import Job, JobGroup

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_CHAR, CHECK_MIN, CHECK_MAX, CHECK_ONLYSPACE, \
    CHECK_UNIQUE

from karesansui.lib.utils import is_param, is_empty, available_virt_uris

def validates_network(obj, network_name=None):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'name'):
        check = False
        checker.add_error(_('Specify network name.'))
    else:
        check = checker.check_network_name(
            _('Network Name'),
            obj.input.name,
            CHECK_EMPTY | CHECK_VALID,
            ) and check

    if not is_param(obj.input, 'cidr'):
        check = False
        checker.add_error(_('Specify bridge IP address for the network.'))
    else:
        check = checker.check_ipaddr(
                _('Bridge IP Address/Netmask'),
                obj.input.cidr,
                CHECK_EMPTY | CHECK_VALID,
                ) and check

    if not is_param(obj.input, 'bridge'):
        check = False
        checker.add_error(_('Specify bridge name to create for the network.'))
    else:
        check = checker.check_netdev_name(
                _('Bridge Device Name'),
                obj.input.bridge,
                CHECK_EMPTY | CHECK_VALID,
                ) and check

    A = is_param(obj.input, 'dhcp_start')
    B = is_param(obj.input, 'dhcp_end')
    #if not ( ((not A) and (not B)) or (A and B)):
    if not (A and B):
        check = False
        checker.add_error(_('Specify both %s and %s') % (_('DHCP Start Address'), _('DHCP End Address')))

    if is_param(obj.input, 'dhcp_start'):
        check = checker.check_ipaddr(
                _('DHCP Start Address'),
                obj.input.dhcp_start,
                CHECK_EMPTY | CHECK_ONLYSPACE | CHECK_VALID,
                ) and check

    if is_param(obj.input, 'dhcp_end'):
        check = checker.check_ipaddr(
                _('DHCP End Address'),
                obj.input.dhcp_end,
                CHECK_EMPTY | CHECK_ONLYSPACE | CHECK_VALID,
                ) and check

    check = checker.check_if_ips_are_in_network(
                            [ _('DHCP Start Address'), _('DHCP End Address'), _('Bridge IP Address/Netmask')],
                            [obj.input.dhcp_start, obj.input.dhcp_end],
                            obj.input.cidr,
                            CHECK_VALID | CHECK_UNIQUE) and check

    check = checker.check_ip_range(
                            [ _('DHCP Start Address'), _('DHCP End Address'), _('Bridge IP Address/Netmask')],
                            [obj.input.dhcp_start, obj.input.dhcp_end, obj.input.cidr],
                            CHECK_VALID) and check

    check = checker.check_virt_network_address_conflict(
                            _('Bridge IP Address/Netmask'),
                            obj.input.cidr,
                            [network_name],   # names to ignore
                            CHECK_VALID) and check

    if is_param(obj.input, 'forward_mode'):
        check = checker.check_forward_mode(
                _('Forward Mode'),
                obj.input.forward_mode,
                CHECK_VALID,
                ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1Network(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        model = findbyhost1(self.orm, host_id)

        uris = available_virt_uris()
        if model.attribute == 0 and model.hypervisor == 1:
            uri = uris["XEN"]
        elif model.attribute == 0 and model.hypervisor == 2:
            uri = uris["KVM"]
        else:
            uri = None

        # if input mode then return empty form
        if self.is_mode_input():
            self.view.host_id = host_id
            self.view.network = dict(name='', cidr='',
                                     dhcp_start='', dhcp_end='',
                                     forward_dev='', forward_mode='',
                                     bridge='')
            return True
        else:
            kvc = KaresansuiVirtConnection(uri)
            try:
                labelfunc = (('active', kvc.list_active_network),
                             ('inactive', kvc.list_inactive_network),
                             )
                # networks = {'active': [], 'inactive': []}
                networks = []
                for label, func in labelfunc:
                    for name in func():
                        try:
                            network = kvc.search_kvn_networks(name)[0] # throws KaresansuiVirtException
                            info = network.get_info()
                            # networks[label].append(info)
                            if info['is_active']:
                                info['activity'] = 'Active'
                            else:
                                info['activity'] = 'Inactive'
                            networks.append(info)
                        except KaresansuiVirtException, e:
                            # network not found
                            pass
            finally:
                kvc.close()

            self.view.networks = networks
            return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        model = findbyhost1(self.orm, host_id)

        uris = available_virt_uris()
        if model.attribute == 0 and model.hypervisor == 1:
            uri = uris["XEN"]
        elif model.attribute == 0 and model.hypervisor == 2:
            uri = uris["KVM"]
        else:
            uri = None

        if not validates_network(self):
            self.logger.debug("Network creation failed. Did not validate.")
            return web.badrequest(self.view.alert)

        name       = self.input.name
        cidr       = self.input.cidr
        dhcp_start = self.input.dhcp_start
        dhcp_end   = self.input.dhcp_end
        bridge     = self.input.bridge

        # We support only 'nat' for forward-mode.
        forward_mode = ''
        if is_param(self.input, 'forward_mode'):
            if self.input.forward_mode == 'nat':
                forward_mode = 'nat'

        try:
            autostart = self.input.autostart
        except:
            autostart = "no"

        # Check if the name is available (not already used).
        kvc = KaresansuiVirtConnection(uri)
        try:
            try:
                kvc.search_kvn_networks(name)
                self.logger.debug("Network name '%s' already used." % name)
                url = '%s/%s/%s.part' % (web.ctx.home, web.ctx.path, name)
                self.logger.debug("Returning url %s as Location." % url)
                return web.conflict(url)
            except KaresansuiVirtException, e:
                # OK
                pass
        finally:
            kvc.close()

        # spin off create job
        options = {'dhcp-start': dhcp_start,
                   'dhcp-end'  : dhcp_end,
                   'bridge-name'    : bridge,
                   'forward-mode'   : forward_mode,
                   'autostart' : autostart,
                  }

        self.logger.debug('spinning off network_create_job name=%s, cidr=%s, options=%s' % (name, cidr, options))
        host = findbyhost1(self.orm, host_id)
        #network_create_job(self, name, cidr, host, options)

        options['name'] = name
        options['cidr'] = cidr

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_CREATE_NETWORK), options)

        # Job Registration
        _jobgroup = JobGroup('Create Network: %s' % name, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('Create Network', 0, _cmd))
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

        self.logger.debug('(Create network) Job group id==%s', _jobgroup.id)
        url = '%s/job/%s.part' % (web.ctx.home, _jobgroup.id)
        self.logger.debug('Returning Location: %s' % url)

        return web.accepted()

urls = (
    '/host/(\d+)/network[/]?(\.html|\.part|\.json)?$', HostBy1Network,
    )

