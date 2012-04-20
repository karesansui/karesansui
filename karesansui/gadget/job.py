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
import simplejson as json
from karesansui.lib.rest import Rest, auth
from karesansui.lib.search import validates_jobsearch
from karesansui.lib.const import JOB_LIST_RANGE, DEFAULT_LANGS, MACHINE_HYPERVISOR
from karesansui.lib.pager import Pager
from karesansui.lib.utils import str2datetime, is_param, is_empty
from karesansui.db.access._2pysilhouette import jg_findbyalltype, jg_findby1

from karesansui.db.access.machine_machine2jobgroup import \
     findbyall as m2mj_findbyall, findbyjobgroup_id1 as m2mj_findby1

from karesansui.db.access.user import findbyname_BM

from karesansui.db.model._2pysilhouette import \
     Job, JobGroup, JOBGROUP_STATUS, JOBGROUP_TYPE

class Job(Rest):

    @auth
    def _GET(self, *param, **params):
        (check, edit) = validates_jobsearch(self)
        if check is False:
            return web.badrequest(self.view.alert)

        if edit is True:
            # user search
            users = findbyname_BM(self.orm, self.input.user)
            users_id = []
            for user in users:
                users_id.append(user.id)

            machine_name = self.input.name.strip()
            if is_empty(machine_name):
                machine_name = None
            
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
            m_m2js = m2mj_findbyall(self.orm,
                           machine_name,
                           start,
                           end,
                           users_id,
                           True
                           )
            if not m_m2js:
                self.logger.debug("Search m_m2js failed. "
                                  "Did not exist m_m2js that in accord with these query. "
                                  "name %s, user_id %s, start %s, end %s" % (machine_name, users_id, start, end))
                return web.nocontent()
            
            self.view.m_m2js = m_m2js
            self.view.name = self.input.name
            self.view.user = self.input.user
            self.view.status = self.input.status
            self.view.start = self.input.start
            self.view.end = self.input.end

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
                                  "Did not exist jobgroups that in accord with these query. "
                                  "jobgroup_ids %s, jobgroup_status %s" % (jobgroup_ids, jobgroup_status))
                return web.nocontent()
            
        else:
            m_m2js = m2mj_findbyall(self.orm)
            self.view.m_m2js = m_m2js
            self.view.name   = ''
            self.view.user   = ''
            self.view.status = ''
            self.view.start  = ''
            self.view.end    = ''

            self.view.m_m2js = m_m2js

            jobgroup_ids = []
            for m_m2j in m_m2js:
                 jobgroup_ids.append(m_m2j[1].jobgroup_id)
                 
            jobgroups = jg_findbyalltype(self.pysilhouette.orm, JOBGROUP_TYPE["SERIAL"],
                                         jobgroup_ids, desc=True)
        
        self.view.JOBGROUP_STATUS = JOBGROUP_STATUS
        self.view.HYPERVISOR = MACHINE_HYPERVISOR
 
        if self.input.has_key('p') is True:
            start = int(self.input.p)
        else:
            start = 0
        self.view.date_format = DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][1] 
        self.view.pager = Pager(jobgroups, start, JOB_LIST_RANGE)

        return True


class JobBy1(Rest):
    
    @auth
    def _GET(self, *param, **params):
        jg_id = param[0]
        jg = jg_findby1(self.pysilhouette.orm, jg_id)
        if jg is None:
            return web.notfound()
        m2mj = m2mj_findby1(self.orm, jg.id)

        self.view.jg = jg
        self.view.m2mj = m2mj
        self.view.JOBGROUP_STATUS = JOBGROUP_STATUS
        self.view.HYPERVISOR = MACHINE_HYPERVISOR
        self.view.date_format = DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][1] 
        self.view.job_count = len(jg.jobs)

        return True

urls = (
    '/job/(\d+)/?(\.part)$', JobBy1,
    '/job/?(\.part)$', Job,
    )
