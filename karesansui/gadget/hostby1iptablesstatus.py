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
from karesansui.lib.const import IPTABLES_COMMAND_CONTROL
from karesansui.lib.rest import Rest, auth
from karesansui.lib.utils import is_param
from karesansui.lib.checker import \
    Checker, CHECK_EMPTY, CHECK_VALID

from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import jg_save
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

IPTABLES_ACTION_START = 1<<0
IPTABLES_ACTION_STOP  = 1<<1

IPTABLES_STATUS = {
    "START"   :1, 
    "STOP"    :2, 
    "RESTART" :3
}

# lib public
def iptables_control(obj, model, action='',options={}):
    if action != "":
        options['action'] = action

    if action == "restart":
        action_msg = "Restart iptables"
    elif action == "start":
        action_msg = "Start iptables"
        msg = "Start iptables"
    elif action == "stop":
        action_msg = "Stop iptables"

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], IPTABLES_COMMAND_CONTROL), options)
        
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

def validates_iptables_status(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'status'):
        check = checker.check_status(
                _('Status'),
                obj.input.status,
                CHECK_EMPTY | CHECK_VALID,
                list(IPTABLES_STATUS.values())
            ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Status'))

    obj.view.alert = checker.errors

    return check

class HostBy1IptablesStatus(Rest):
    
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

        if not validates_iptables_status(self):
            return web.badrequest(self.view.alert)

        status = int(self.input.status)

        model = findbyhost1(self.orm, host_id)

        ret = False
        if status & IPTABLES_ACTION_STOP and status & IPTABLES_ACTION_START:
            ret = iptables_control(self, model, 'restart')

        elif status & IPTABLES_ACTION_STOP:
            ret = iptables_control(self, model, 'stop')

        elif status & IPTABLES_ACTION_START:
            ret = iptables_control(self, model, 'start')

        if ret is True:
            return web.accepted(url=web.ctx.path)
        else:
            return False

urls = (
    '/host/(\d+)/iptables/status/?(\.part)$', HostBy1IptablesStatus,
    )
