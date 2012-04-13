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

import web
import simplejson as json

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import VIRT_COMMAND_DELETE_NETWORK, VIRT_COMMAND_UPDATE_NETWORK
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

    if not network_name:
        check = False
        checker.add_error(_('Specify network name.'))

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

class HostBy1NetworkBy1(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        network_name = param[1]
        if not (network_name and host_id):
            return web.badrequest()

        kvc = KaresansuiVirtConnection()
        try:
            try:
                network = kvc.search_kvn_networks(network_name)[0] # throws KaresansuiVirtException
                info = network.get_info()
            except KaresansuiVirtException, e:
                # network not found
                self.logger.debug("Network not found. name=%s" % network_name)
                return web.notfound()
        finally:
            kvc.close()

        cidr = '%s/%s' % (info['ip']['address'], info['ip']['netmask'])
        network = dict(name=info['name'],
                       cidr=cidr,
                       dhcp_start=info['dhcp']['start'],
                       dhcp_end=info['dhcp']['end'],
                       forward_dev=info['forward']['dev'],
                       forward_mode=info['forward']['mode'],
                       bridge=info['bridge']['name'],
                       )
        self.view.info = info
        self.view.network = network
        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        network_name = param[1]
        if not network_name:
            self.logger.debug("Network update failed. Network not found.")
            return web.notfound("Network not found.")

        if not validates_network(self, network_name=network_name):
            self.logger.debug("Network update failed. Did not validate.")
            return web.badrequest(self.view.alert)

        cidr       = self.input.cidr
        dhcp_start = self.input.dhcp_start
        dhcp_end   = self.input.dhcp_end
        bridge     = self.input.bridge
        forward_mode = getattr(self.input, 'forward_mode', '')

        try:
            autostart = self.input.autostart
        except:
            autostart = "no"

        #
        # spin off update job
        #
        options = {'name' : network_name,
                   'cidr': cidr,
                   'dhcp-start': dhcp_start,
                   'dhcp-end' : dhcp_end,
                   'bridge-name' : bridge,
                   'forward-mode' : forward_mode,
                   'autostart' : autostart,
                   }

        self.logger.debug('spinning off network_update_job options=%s' % (options))

        host = findbyhost1(self.orm, host_id)

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_UPDATE_NETWORK), options)

        # Job Registration
        _jobgroup = JobGroup('Update network: %s' % network_name, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('Update network', 0, _cmd))

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

        self.logger.debug('(Update network) Job group id==%s', _jobgroup.id)
        url = '%s/job/%s.part' % (web.ctx.home, _jobgroup.id)
        self.logger.debug('Returning Location: %s' % url)

        return web.accepted(url=url)

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        network_name = param[1]
        if not network_name:
            self.logger.debug("Network delete failed. Network not found.")
            return web.notfound("Network not found.")

        if network_name == 'default':
            self.logger.debug('Network delete failed. Target network is "default".')
            return web.badrequest('Target network "default" can not deleted.')

        host = findbyhost1(self.orm, host_id)

        options = {}
        options['name'] = network_name
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_NETWORK), options)

        # Job Registration
        _jobgroup = JobGroup('Delete network: %s' % network_name, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('Delete network', 0, _cmd))

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

        self.logger.debug('(Delete network) Job group id==%s', _jobgroup.id)
        url = '%s/job/%s.part' % (web.ctx.home, _jobgroup.id)
        self.logger.debug('Returning Location: %s' % url)

        return web.accepted()

urls = (
    '/host/(\d+)/network/([^\./]+)[/]?(\.html|\.part|\.json)?$', HostBy1NetworkBy1,
    )

