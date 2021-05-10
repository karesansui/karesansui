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

import karesansui
from karesansui.lib.const import VIRT_COMMAND_ADD_NIC
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID
from karesansui.lib.utils import is_param
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

# lib public 
def validates_nic(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []
    
    # nic_type - [phydev, virnet]
    if is_param(obj.input, 'nic_type'):
        if (obj.input.nic_type in ['phydev', 'virnet']) is False:
            check = False
            checker.add_error(_(""))
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Interface Type'))
            
    # mac_address
    if is_param(obj.input, 'mac_address'):
        check = checker.check_macaddr(
            _('MAC Address'),
            obj.input.mac_address,
            CHECK_EMPTY | CHECK_VALID
            ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('MAC Address'))

    obj.view.alert = checker.errors

    return check

def create_nic_job(obj, guest, name, mac, bridge, network, options={}):
    options['name'] = name
    options['mac'] = mac
    if bridge is not None:
        options['bridge'] = bridge
    if network is not None:
        options['network'] = network

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_ADD_NIC), options)

    cmdname = "Create NIC"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job('%s command' % cmdname, 0, _cmd))
    
    _machine2jobgroup = m2j_new(machine=guest,
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
