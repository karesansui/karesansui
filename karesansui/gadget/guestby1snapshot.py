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
import stat
import time

import web
import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import \
     VIRT_COMMAND_TAKE_SNAPSHOT, \
     NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH,\
     VIRT_XML_CONFIG_DIR
from karesansui.lib.utils import is_param
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX, \
     CHECK_LENGTH, CHECK_ONLYSPACE

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access.notebook import new as new_notebook
from karesansui.db.access.snapshot import new as new_snapshot, \
     save as save_snapshot, \
     findbyname_guestby1 as s_findbyname_guestby1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot

from pysilhouette.command import dict2command
from karesansui.db.model._2pysilhouette import Job, JobGroup

def validates_snapshot(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []
    
    if is_param(obj.input, 'title'):
        check = checker.check_string(
                    _('Title'),
                    obj.input.title,
                    CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = NOTE_TITLE_MIN_LENGTH,
                    max = NOTE_TITLE_MAX_LENGTH,
                ) and check

    if is_param(obj.input, 'value'):
        check = checker.check_string(
                    _('Note'),
                    obj.input.value,
                    CHECK_ONLYSPACE,
                    None,
                    None,
                    None,
                ) and check

    obj.view.alert = checker.errors
    
    return check

class GuestBy1Snapshot(Rest):

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        guest = findbyguest1(self.orm, guest_id)

        kvs = KaresansuiVirtSnapshot(readonly=False)
        try:
            domname = kvs.kvc.uuid_to_domname(guest.uniq_key)
            if not domname: return web.notfound()

            if self.is_mode_input():
                virt = kvs.kvc.search_kvg_guests(domname)[0]
                if virt.is_active() is True:
                    return web.badrequest(_("Guest is running. Please stop and try again. name=%s" % domname))

            self.view.is_creatable = kvs.isSupportedDomain(domname)

            self.view.snapshot_error_msg = ''
            if self.view.is_creatable is not True and len(kvs.error_msg) > 0:
                self.view.snapshot_error_msg = ", ".join(kvs.error_msg)

            try:
                snapshot_list = kvs.listNames(domname)[domname]
            except:
                pass

            current_snapshot = kvs.getCurrentSnapshotName(domname)

        finally:
            kvs.finish()

        snapshots = []
        if snapshot_list:
            snapshot_list.sort(reverse = True)
            for snapshot in snapshot_list:
                model = s_findbyname_guestby1(self.orm, snapshot,guest_id)
                if model is None:
                    name           = snapshot
                    notebook_title = ""
                    created_user   = _("N/A")
                    created        = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(snapshot)))
                else:
                    name           = model.name
                    notebook_title = model.notebook.title
                    created_user   = model.created_user.nickname
                    created        = model.created

                current = False
                if snapshot == current_snapshot:
                    current = True

                snapshots.append((name,
                                  notebook_title,
                                  domname,
                                  created_user,
                                  created,
                                  current
                                  ))

        self.view.snapshots = snapshots
        self.view.guest = guest
            
        return True

    @auth
    def _POST(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if not validates_snapshot(self): 
            return web.badrequest(self.view.alert)
        
        guest = findbyguest1(self.orm, guest_id)

        kvs = KaresansuiVirtSnapshot(readonly=False)
        try:
            domname = kvs.kvc.uuid_to_domname(guest.uniq_key)
            if not domname: return web.conflict(web.ctx.path)

            virt = kvs.kvc.search_kvg_guests(domname)[0]
            if virt.is_active() is True:
                return web.badrequest(_("Guest is running. Please stop and try again. name=%s" % domname))

        finally:
            kvs.finish()

        id = int(time.time())
        notebook = new_notebook(self.input.title, self.input.value)
        snapshot = new_snapshot(guest, id, self.me, self.me, notebook)
        save_snapshot(self.orm, snapshot)

        options = {}
        options['name'] = domname
        options['id'] = id

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_TAKE_SNAPSHOT),
            options)

        cmdname = 'Take Snapshot'
        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('%s command' % cmdname, 0, _cmd))

        _machine2jobgroup = m2j_new(machine=guest,
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
    '/host/(\d+)/guest/(\d+)/snapshot/?(\.part)?$', GuestBy1Snapshot,
    )
