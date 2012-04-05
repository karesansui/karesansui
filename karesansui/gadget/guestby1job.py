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

import web

import karesansui
from karesansui.lib.search import validates_jobsearch
from karesansui.lib.rest import Rest, auth
from karesansui.lib.pager import Pager, validates_page
from karesansui.lib.utils import str2datetime, is_param, is_empty
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection

from karesansui.lib.checker import Checker,\
    CHECK_EMPTY, CHECK_VALID, \
    CHECK_LENGTH, CHECK_ONLYSPACE,\
    CHECK_MIN, CHECK_MAX
from karesansui.lib.const import JOB_LIST_RANGE, DEFAULT_LANGS,\
    USER_MIN_LENGTH, USER_MAX_LENGTH,\
    ID_MIN_LENGTH, ID_MAX_LENGTH, \
    MACHINE_HYPERVISOR

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access._2pysilhouette import jg_findbyalltype
from karesansui.db.access.machine_machine2jobgroup import findbyguest as m2mj_findbyguest
from karesansui.db.access.user import findbyname_BM
from karesansui.db.model._2pysilhouette import JOBGROUP_STATUS, JOBGROUP_TYPE

class GuestBy1Job(Rest):

    @auth
    def _GET(self, *param, **params):

        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()
        
        model = findbyguest1(self.orm, guest_id)
        # virt
        self.kvc = KaresansuiVirtConnection()
        try:
            domname = self.kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()
        finally:
            self.kvc.close()


        (check, edit) = validates_jobsearch(self)
        if check is False:
            return web.badrequest(self.view.alert)

        if edit is True:
            # user search
            users = findbyname_BM(self.orm, self.input.user)
            users_id = []

            for user in users:
                users_id.append(user.id)
            if is_empty(self.input.start):
                start = None
            else:
                start = str2datetime(self.input.start,
                                     DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0])
            if is_empty(self.input.end):
                end = None
            else:
                end = str2datetime(self.input.end,
                                   DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0],True)

            # machine search
            m_m2js = m2mj_findbyguest(self.orm,
                           guest_id,
                           start,
                           end,
                           users_id,
                           )
            if not m_m2js:
                self.logger.debug("Search m_m2js failed. "
                                  "Did not exist m_m2js that in accord with these query. "
                                  "guest_id %s, start %s, end %s, users_id %s" % (guest_id, start, end, users_id))
                return web.nocontent()
            
            self.view.m_m2js = m_m2js
            self.view.user   = self.input.user
            self.view.status = self.input.status
            self.view.start  = self.input.start
            self.view.end    = self.input.end

            jobgroup_ids = []
            for m_m2j in m_m2js:
                jobgroup_ids.append(m_m2j[1].jobgroup_id)

            jobgroup_status = self.input.status
            if is_empty(jobgroup_status):
                jobgroup_status = None
            jobgroups = jg_findbyalltype(self.pysilhouette.orm, JOBGROUP_TYPE["SERIAL"],
                                         jobgroup_ids, jobgroup_status, desc=True)
            if not jobgroups:
                self.logger.debug("Search jobgroups failed. "
                                  "Did not exist jobgroups that in accord with these query."
                                  "jobgroup_ids %s, jobgroup_status %s" % (jobgroup_ids, jobgroup_status))
                return web.nocontent()
        else:
            m_m2js = m2mj_findbyguest(self.orm, guest_id)

            self.view.m_m2js = m_m2js
            self.view.user   = ''
            self.view.status = ''
            self.view.start  = ''
            self.view.end    = ''

            jobgroup_ids = []
            for m_m2j in m_m2js:
                 jobgroup_ids.append(m_m2j[1].jobgroup_id)

            jobgroups = jg_findbyalltype(self.pysilhouette.orm, JOBGROUP_TYPE["SERIAL"],
                         jobgroup_ids, desc=True)

        self.view.JOBGROUP_STATUS = JOBGROUP_STATUS
        self.view.HYPERVISOR = MACHINE_HYPERVISOR

        if self.input.has_key('p') is True:
            if validates_page(self) is True:
                start = int(self.input.p)
            else:
                return web.badrequest(self.view.alert)

        else:
            start = 0
        self.view.date_format = DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][1]
        self.view.pager = Pager(jobgroups, start, JOB_LIST_RANGE)

        return True

urls = (
    '/host/(\d+)/guest/(\d+)/job/?(\.part)$', GuestBy1Job,
    )
