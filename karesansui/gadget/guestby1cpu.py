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
from karesansui.lib.rest import Rest, auth

from karesansui.lib.const import VIRT_COMMAND_SET_VCPUS, VCPUS_MIN_SIZE
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.utils import is_int, is_param, is_empty
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_MIN

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access.machine import findbyguest1
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command


def validates_cpu(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'max_vcpus'):
        check = checker.check_number(
                _('Maximum Allocatable Virtual CPUs'),
                obj.input.max_vcpus,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                min = VCPUS_MIN_SIZE,
                ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Maximum Allocatable Virtual CPUs'))

    if is_param(obj.input, 'vcpus'):
        check = checker.check_number(
                _("Number of Virtual CPUs to Allocate"),
                obj.input.vcpus,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                min = VCPUS_MIN_SIZE,
                ) and check;

    obj.view.alert = checker.errors
    return check



class GuestBy1Cpu(Rest):
    
    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()

            virt = kvc.search_kvg_guests(domname)[0]

            vcpus_info = virt.get_vcpus_info()
            self.view.max_vcpus_limit = kvc.get_max_vcpus()
            self.view.max_vcpus       = vcpus_info['bootup_vcpus']
            self.view.vcpus_limit     = vcpus_info['max_vcpus']
            self.view.vcpus           = vcpus_info['vcpus']

            self.view.cpuTime = virt.get_info()['cpuTime']
            self.view.hypervisor = virt.get_info()['hypervisor']

            self.view.guest = model
        finally:
            kvc.close()
            
        return True


    @auth
    def _PUT(self, *param, **params):
        """<comment-ja>
        Japanese Comment
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if not validates_cpu(self):
            return web.badrequest(self.view.alert)
        
        if is_param(self.input, 'vcpus'):
            vcpus = int(self.input.vcpus)
        else:
            vcpus = None
        max_vcpus = int(self.input.max_vcpus)

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]

            vcpus_info = virt.get_vcpus_info()
            max_vcpus_limit = kvc.get_max_vcpus()
            vcpus_limit     = vcpus_info['max_vcpus']
        finally:
            kvc.close()
                
        if max_vcpus_limit < max_vcpus:
            return web.badrequest("%s is greater than the maximum number supported for guest. - max_vcpus_limit=%d max_vcpus=%d" \
                % (_('Maximum Number of Virtual CPUs'), self.input.max_vcpus_limit,self.input.max_vcpus,))

        if vcpus is not None:
            if vcpus_limit < vcpus:
                return web.badrequest("%s is greater than the maximum number supported for guest. - vcpus_limit=%d vcpus=%d" \
                    % (_('Number of Virtual CPUs'), self.input.vcpus_limit,self.input.vcpus,))

        options = {}
        options["name"] = domname
        if vcpus is not None:
            options["vcpus"] = vcpus
        options["max-vcpus"] = max_vcpus
        
        _cmd = dict2command("%s/%s" % (karesansui.config['application.bin.dir'],
                                       VIRT_COMMAND_SET_VCPUS),
                            options)
        
        cmdname = "Set CPU"
        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('%s command' % cmdname, 0, _cmd))
        
        _machine2jobgroup = m2j_new(machine=model,
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
            

urls = ('/host/(\d+)/guest/(\d+)/cpu/?(\.part)$', GuestBy1Cpu,)
