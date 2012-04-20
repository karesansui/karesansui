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

import web
import simplejson as json

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import VIRT_COMMAND_APPLY_SNAPSHOT
from karesansui.lib.utils import is_param, is_int

from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot

from karesansui.db.access.machine  import findbyguest1
from karesansui.db.access.snapshot import findbyname_guestby1 as s_findbyname_guestby1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from karesansui.db.model._2pysilhouette import Job, JobGroup
from pysilhouette.command import dict2command

class GuestBy1CurrentSnapshot(Rest):

    @auth
    def _PUT(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_param(self.input, 'id') is False \
            or is_int(self.input.id) is False:
            return web.badrequest("Request data is invalid.")

        snapshot_id = str(self.input.id)

        snapshot = s_findbyname_guestby1(self.orm, snapshot_id, guest_id)
        if snapshot is None:
            pass
            # ignore snapshots that is not in database.
            #return web.badrequest("Request data is invalid.")

        model = findbyguest1(self.orm, guest_id)

        kvs = KaresansuiVirtSnapshot(readonly=False)
        snapshot_list = []
        try:
            domname = kvs.kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()
            self.view.is_creatable = kvs.isSupportedDomain(domname)
            try:
                snapshot_list = kvs.listNames(domname)[domname]
            except:
                pass

        finally:
            kvs.finish()

        if not snapshot_id in snapshot_list:
            self.logger.debug(_("The specified snapshot does not exist in database. - %s") % snapshot_id)
            # ignore snapshots that is not in database.
            #return web.notfound()

        action_cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'],
                       VIRT_COMMAND_APPLY_SNAPSHOT),
            {"name" : domname, "id" : snapshot_id})

        cmdname = 'Apply Snapshot'

        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _job = Job('%s command' % cmdname, 0, action_cmd)
        _jobgroup.jobs.append(_job)

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

        self.view.currentsnapshot = snapshot

        return web.accepted(url=web.ctx.path)

urls = (
    '/host/(\d+)/guest/(\d+)/currentsnapshot/?(\.part)?$', GuestBy1CurrentSnapshot,
    )
