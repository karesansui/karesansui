# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import os
import time

import web

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import VIRT_COMMAND_DELETE_SNAPSHOT, \
     ID_MIN_LENGTH, ID_MAX_LENGTH, \
     NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH

from karesansui.lib.utils import is_param, json_dumps
from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX, \
    CHECK_LENGTH, CHECK_ONLYSPACE

from karesansui.db.access.notebook import new as new_notebook
from karesansui.db.access.snapshot import new as new_snapshot

from karesansui.db.access.machine  import findbyguest1 as m_findbyguest1
from karesansui.db.access.snapshot import findby1 as s_findby1, \
     findbyname_guestby1 as s_findbyname_guestby1, \
     logical_delete, save as save_snapshot

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new

from karesansui.db.model._2pysilhouette import Job, JobGroup
from pysilhouette.command import dict2command

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
    
def validates_param_id(obj, snapshot_id):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    check = checker.check_number(
            _('Snapshot ID'),
            snapshot_id,
            CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
            min = ID_MIN_LENGTH,
            max = ID_MAX_LENGTH,
        ) and check
    
    obj.view.alert = checker.errors

    return check

class GuestBy1SnapshotBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()
        
        snapshot_id = param[2]
        if not validates_param_id(self, snapshot_id):
            return web.notfound(self.view.alert)

        guest = m_findbyguest1(self.orm, guest_id)
        if not guest:
            return web.notfound()

        kvs = KaresansuiVirtSnapshot(readonly=False)
        snapshot_list = []
        try:
            domname = kvs.kvc.uuid_to_domname(guest.uniq_key)
            if not domname: return web.notfound()
            self.view.is_creatable = kvs.isSupportedDomain(domname)
            try:
                snapshot_list = kvs.listNames(domname)[domname]
            except:
                pass

            parent_name  = kvs.getParentName(snapshot_id,domain=domname)
            if parent_name is None:
                parent_name = _('None')
            children_names = kvs.getChildrenNames(snapshot_id,domain=domname)
            if len(children_names) == 0:
                children_name = _('None')
            else:
                children_name = ",".join(children_names)

            model = s_findbyname_guestby1(self.orm, snapshot_id, guest_id)
            if model is None:
                name           = snapshot_id
                notebook_title = ""
                notebook_value = ""
                created_user   = _("N/A")
                created        = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(snapshot_id)))
                modified_user  = _("N/A")
                modified       = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(snapshot_id)))
            else:
                name           = model.name
                notebook_title = model.notebook.title
                notebook_value = model.notebook.value
                created_user   = model.created_user.nickname
                created        = model.created
                modified_user  = model.modified_user.nickname
                modified       = model.modified

            current_snapshot = kvs.getCurrentSnapshotName(domname)

            current = False
            if snapshot_id == current_snapshot:
                current = True

        finally:
            kvs.finish()

        if not snapshot_id in snapshot_list:
            self.logger.error(_("The specified snapshot does not exist. - %s") % snapshot_id)
            return web.notfound()

        if self.__template__["media"] == 'json':
            self.view.snapshot = json_dumps((
                                  snapshot_id,
                                  notebook_title,
                                  notebook_value,
                                  domname,
                                  created_user,
                                  created,
                                  modified_user,
                                  modified,
                                  current,
                                  parent_name,
                                  children_name,
                                 ))
        else:
            self.view.snapshot = (snapshot_id,
                                  notebook_title,
                                  notebook_value,
                                  domname,
                                  created_user,
                                  created,
                                  modified_user,
                                  modified,
                                  current,
                                  parent_name,
                                  children_name,
                                  )
        return True

    @auth
    def _PUT(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        snapshot_id = param[2]
        if not validates_param_id(self, snapshot_id):
            return web.notfound(self.view.alert)

        if not validates_snapshot(self):
            return web.badrequest(self.view.alert)

        guest = m_findbyguest1(self.orm, guest_id)
        if not guest:
            return web.notfound()

        snapshot = s_findbyname_guestby1(self.orm, snapshot_id, guest_id)
        if not snapshot:
            notebook = new_notebook(self.input.title, self.input.value)
            snapshot = new_snapshot(guest, int(snapshot_id), self.me, self.me, notebook)
            save_snapshot(self.orm, snapshot)
        else:
            snapshot.notebook.title = self.input.title
            snapshot.notebook.value = self.input.value

        return web.seeother(web.ctx.path)
    
    @auth
    def _DELETE(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        snapshot_id = param[2]
        if not validates_param_id(self, snapshot_id):
            return web.notfound(self.view.alert)

        guest = m_findbyguest1(self.orm, guest_id)
        if not guest:
            return web.notfound()

        kvs = KaresansuiVirtSnapshot(readonly=False)
        snapshot_list = []
        try:
            domname = kvs.kvc.uuid_to_domname(guest.uniq_key)
            if not domname: return web.notfound()
            self.view.is_creatable = kvs.isSupportedDomain(domname)
            try:
                snapshot_list = kvs.listNames(domname)[domname]
            except:
                pass

            current_snapshot = kvs.getCurrentSnapshotName(domname)

        finally:
            kvs.finish()

        if not snapshot_id in snapshot_list:
            self.logger.error(_("The specified snapshot does not exist. - %s") % snapshot_id)
            return web.notfound()

        # delete
        action_cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'],
                       VIRT_COMMAND_DELETE_SNAPSHOT),
            {"name" : domname, "id" : snapshot_id})

        cmdname = 'Delete Snapshot'
        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _job = Job('%s command' % cmdname, 0, action_cmd)
        _jobgroup.jobs.append(_job)
        
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

        snapshot = s_findbyname_guestby1(self.orm, snapshot_id, guest_id)
        if snapshot:
            logical_delete(self.orm, snapshot)

        return web.accepted()

urls = (
    '/host/(\d+)/guest/(\d+)/snapshot/(\d+)/?(\.part|\.json)?$', GuestBy1SnapshotBy1,
    )
