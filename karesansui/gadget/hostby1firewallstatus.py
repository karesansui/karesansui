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

import simplejson as json
import web

import karesansui
from karesansui.lib.const import FIREWALL_COMMAND_SAVE_FIREWALL, \
                                 FIREWALL_COMMAND_RESTORE_FIREWALL
from karesansui.lib.rest import Rest, auth
from karesansui.lib.firewall.iptables import KaresansuiIpTables
from karesansui.lib.utils import is_param
from karesansui.lib.checker import \
    Checker, CHECK_EMPTY, CHECK_VALID

from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import jg_save
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

FIREWALL_ACTION_INIT  = 0
FIREWALL_ACTION_START = 1<<0
FIREWALL_ACTION_STOP  = 1<<1

FIREWALL_STATUS = {
    "READ":0, 
    "START":1, 
    "STOP":2, 
    "RESTART":3
}

# lib public
def firewall_restore(obj, model, action='',options={}):
    if action != "":
        options['action'] = action

    if action == "restart":
        action_msg = "Restart Firewall"
    elif action == "start":
        action_msg = "Start Firewall"
    elif action == "stop":
        action_msg = "Stop Firewall"
    else:
        action_msg = "Restore Firewall"

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], FIREWALL_COMMAND_RESTORE_FIREWALL), options)
        
    _jobgroup = JobGroup(action_msg, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job("%s command" % action_msg, 0, _cmd))
    
    _machine2jobgroup = m2j_new(machine=model,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )
    
    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )

    return True

def firewall_save(obj, model, options={}):

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], FIREWALL_COMMAND_SAVE_FIREWALL), options)

    cmdname = u"Initialize Firewall"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job("%s command" % cmdname, 0, _cmd))
    
    _machine2jobgroup = m2j_new(machine=model,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )
    
    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )

    return True

def validates_fw_status(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'status'):
        check = checker.check_status(
                _('Status'),
                obj.input.status,
                CHECK_EMPTY | CHECK_VALID,
                FIREWALL_STATUS.values()
            ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Status'))

    obj.view.alert = checker.errors

    return check

class HostBy1FirewallStatus(Rest):
    
    @auth
    def _PUT(self, *param, **params):
        """<comment-ja>
        ステータス更新
         - param
           - read = 0
           - start = 1
           - stop = 2
           - restart = 3
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_fw_status(self):
            return web.badrequest(self.view.alert)

        status = int(self.input.status)

        kit = KaresansuiIpTables()

        model = findbyhost1(self.orm, host_id)

        ret = False
        if status == FIREWALL_ACTION_INIT:
            ret = firewall_save(self, model)
        elif status & FIREWALL_ACTION_STOP and status & FIREWALL_ACTION_START:
            kit.firewall_xml = kit.read_firewall_xml()
            ret = firewall_restore(self, model, 'restart')

        elif status & FIREWALL_ACTION_STOP:
            kit.firewall_xml = kit.read_firewall_xml()
            ret = firewall_restore(self, model, 'stop')

        elif status & FIREWALL_ACTION_START:
            kit.firewall_xml = kit.read_firewall_xml()
            ret = firewall_restore(self, model, 'start')

        if ret is True:
            return web.accepted(url=web.ctx.path)
        else:
            return False

urls = (
    '/host/(\d+)/firewall/status/?(\.part)$', HostBy1FirewallStatus,
    )
