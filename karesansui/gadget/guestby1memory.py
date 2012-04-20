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

from karesansui.lib.const import VIRT_COMMAND_SET_MEMORY
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection

from karesansui.lib.utils import is_param

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access.machine import findbyguest1
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

class GuestBy1Memory(Rest):
    
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
            self.view.info = virt.get_info()
            #self.view.mem_info = kvc.get_mem_info()
            self.view.nodeinfo = kvc.get_nodeinfo()
            self.view.guest = model
            self.view.hypervisor = self.view.info['hypervisor']
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

        if is_param(self.input, 'memory'):
            memory = int(self.input.memory)
        else:
            memory = None
        max_memory = int(self.input.max_memory)

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            info = virt.get_info()
            #maxMem = info["maxMem"]
            now_memory = info["memory"]
            mem_info = kvc.get_mem_info()
            nodeinfo = kvc.get_nodeinfo()
        finally:
            kvc.close()
            
        # valid
        #if (mem_info["host_free_mem"] + (now_memory / 1024)) < memory:
        #    return web.badrequest("Memory value is greater than the maximum memory value. - memory=%s" % self.input.memory)

        options = {}
        options["name"] = domname
        options["maxmem"] = max_memory
        if memory is None:
            options["memory"] = max_memory
        else:
            options["memory"] = memory
        _cmd = dict2command("%s/%s" % (karesansui.config['application.bin.dir'],
                                       VIRT_COMMAND_SET_MEMORY),
                            options)
        cmdname = "Set Memory"
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
        return  web.accepted(url=web.ctx.path)

urls = (
    '/host/(\d+)/guest/(\d+)/memory/?(\.part)?$', GuestBy1Memory,
    )
