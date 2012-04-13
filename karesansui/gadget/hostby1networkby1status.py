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

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.utils import json_dumps, is_param
from karesansui.lib.checker import \
    Checker, CHECK_EMPTY, CHECK_VALID

from pysilhouette.command import dict2command

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.model._2pysilhouette import Job, JobGroup

NETWORK_ACTIVE = 1
NETWORK_INACTIVE = 0

def validates_nw_status(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'status'):
        status = int(obj.input.status)
        check = checker.check_status(
                _('Status'),
                status,
                CHECK_EMPTY | CHECK_VALID,
                [NETWORK_ACTIVE, NETWORK_INACTIVE]
            ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Status'))

    obj.view.alert = checker.errors

    return check

class HostBy1NetworkBy1Status(Rest):
    @auth
    def _GET(self, *param, **params):
        """<comment-ja>
        ネットワークがアクティブかどうかのステータス
         - inactive = 0
         - active = 1
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        # TODO valid
        network_name =param[1]
        if not network_name:
            return web.badrequest()

        kvc = KaresansuiVirtConnection()
        try:
            kvn = kvc.search_kvn_networks(network_name)[0]
            status = NETWORK_INACTIVE
            if kvn.is_active():
                status = NETWORK_ACTIVE

            if self.__template__["media"] == 'json':
                self.view.status = json_dumps(status)
            else:
                self.view.status = status

            self.__template__.dir = 'hostby1networkby1'
        finally:
            kvc.close()

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        # TODO valid
        network_name = param[1]
        if not network_name:
            return web.notfound()

        if validates_nw_status(self) is False:
            return web.badrequest(self.view.alert)

        status = int(self.input.status)

        kvc = KaresansuiVirtConnection()
        try:
            kvn = kvc.search_kvn_networks(network_name)[0]
            if status == NETWORK_INACTIVE:
                # Stop network
                network_start_stop_job(self, host_id, network_name, 'stop')
                return web.accepted("/host/%s/network/%s.%s" % (host_id, network_name, self.__template__['media']))
            elif status == NETWORK_ACTIVE:
                # Start network
                network_start_stop_job(self, host_id, network_name, 'start')
                return web.accepted("/host/%s/network/%s.%s" % (host_id, network_name, self.__template__['media']))
            else:
                return web.badrequest()
        finally:
            kvc.close()

def network_start_stop_job(obj, host_id, network_name, action):
    """
    Register start/stop network job into pysilhouette
    @param obj: Rest object
    @param network_name: Name of network to start or stop
    @type network_name: string
    @param action: 'start' or 'stop'
    @type action: string
    """

    if not network_name:
        raise KaresansuiException

    if (karesansui.sheconf.has_key('env.uniqkey') is False) \
           or (karesansui.sheconf['env.uniqkey'].strip('') == ''):
        raise KaresansuiException

    if not (action == 'start' or action == 'stop'):
        raise KaresansuiException

    host = findbyhost1(obj.orm, host_id)

    _cmd = None
    _jobgroup = None
    if action == 'start':
        cmdname = ["Start Network", "start network"]
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], 'restart_network.py'),
            dict(name=network_name, force=None))
    else:
        cmdname = ["Stop Network", "stop network"]
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], 'stop_network.py'),
            dict(name=network_name))

    # Job Register
    _jobgroup = JobGroup(cmdname[0], karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job('%s command' % cmdname[1], 0, _cmd))

    _machine2jobgroup = m2j_new(machine=host,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    # INSERT
    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )


urls = (
    '/host/(\d+)/network/([^/]+)/status?(\.part|\.json)?$', HostBy1NetworkBy1Status,
    )
