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
import datetime
import time

import karesansui
from karesansui.lib.rest import Rest, auth, OUTPUT_TYPE_FILE
from karesansui.lib.utils import is_param, is_empty, \
    str2datetime, create_epochsec, remove_file
from karesansui.lib.rrd.rrd import RRD
from karesansui.lib.const import DEFAULT_LANGS

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID

def validates_report(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'report_start_day'):
        check = checker.check_datetime_string(_('Start Date'),
                                              obj.input.report_start_day,
                                              CHECK_EMPTY | CHECK_VALID,
                                              obj.me.languages,
                                              ) and check

    if is_param(obj.input, 'report_end_day'):
        check = checker.check_datetime_string(_('End Date'),
                                              obj.input.report_end_day,
                                              CHECK_EMPTY | CHECK_VALID,
                                              obj.me.languages,
                                              ) and check

    if is_param(obj.input, 'report_start_time'):
        check = checker.check_time_string(_('Start Time'),
                                          obj.input.report_start_time,
                                          CHECK_EMPTY | CHECK_VALID,
                                          ) and check

    if is_param(obj.input, 'report_end_time'):
        check = checker.check_time_string(_('End Time'),
                                          obj.input.report_end_time,
                                          CHECK_EMPTY | CHECK_VALID,
                                          ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1ReportBy1By1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        target = param[1]
        if target is None: return web.notfound()

        dev = param[2]
        if dev is None: return web.notfound()

        if not validates_report(self):
            self.logger.debug("Get report failed. Did not validate.")
            return web.badrequest(self.view.alert)

        today = datetime.datetime.today()

        if is_param(self.input, 'report_start_day') and not is_empty(self.input.report_start_day):
            start_day = str2datetime(self.input.report_start_day,
                                     DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0])
        else:
            start_day = today - datetime.timedelta(1)

        if is_param(self.input, 'report_start_time') and not is_empty(self.input.report_start_time):
            (start_hour, start_minute) = self.input.report_start_time.split(':',2)
            start_hour = int(start_hour)
            start_minute = int(start_minute)
        else:
            start_hour = today.hour
            start_minute = today.minute

        if is_param(self.input, 'report_end_day') and not is_empty(self.input.report_end_day):
            end_day = str2datetime(self.input.report_end_day,
                                     DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0])
        else:
            end_day = today

        if is_param(self.input, 'report_end_time') and not is_empty(self.input.report_end_time):
            (end_hour, end_minute) = self.input.report_end_time.split(':', 2)
            end_hour = int(end_hour)
            end_minute = int(end_minute)

        else:
            end_hour = today.hour
            end_minute = today.minute

        start_time = create_epochsec(start_day.year,
                                     start_day.month,
                                     start_day.day,
                                     start_hour,
                                     start_minute,
                                     )

        end_time = create_epochsec(end_day.year,
                                   end_day.month,
                                   end_day.day,
                                   end_hour,
                                   end_minute,
                                   )
        if int(start_time) > int(end_time):
            self.logger.error("Getting reports failed. Start time > end time.")
            return web.badrequest(_('Getting reports failed. Start time > end time.'))

        if is_param(self.input, 'type') and not is_empty(self.input.type):
            type = self.input.type
        else:
            type = "default"

        if is_param(self.input, 'host') and not is_empty(self.input.host):
            host = self.input.host
        else:
            host = None

        if is_param(self.input, 'libvirt_target') and not is_empty(self.input.libvirt_target):
            libvirt_target = self.input.libvirt_target
        else:
            libvirt_target = None

        rrd = RRD(self._, self.me.languages)
        if host is not None:
            if rrd.set_rrd_dir_host(host) is False:
                self.logger.debug("Get report failed. Target host not found.")
                return web.notfound()

        filepath = rrd.create_graph(target, dev, type, start_time, end_time, libvirt_target)

        if filepath != "":
            self.download.type = OUTPUT_TYPE_FILE
            self.download.file = filepath
            self.download.once = True

        return True

urls = (
    '/host/(\d+)/report/([a-zA-Z0-9]+)/([a-zA-Z0-9_\.\-]+)(\.png)$', HostBy1ReportBy1By1,
    )
