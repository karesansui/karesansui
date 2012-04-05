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

"""
@authors: Hiroki Takayasu <hiroki@karesansui-project.info>
"""
import os
import web
import socket

from karesansui.lib.rest import Rest, auth
from karesansui.lib.log.config import LogViewConfigParam
from karesansui.lib.const import LOG_VIEW_XML_FILE, DEFAULT_LANGS
from karesansui.lib.utils import json_dumps, is_param, str2datetime, create_epochsec
from karesansui.lib.log.viewer import read_log, read_log_with_lotate

from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_VALID

def validates_log(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 's'):
        check = checker.check_datetime_string(_('Start Date'),
                                              obj.input.s,
                                              CHECK_EMPTY | CHECK_VALID,
                                              obj.me.languages,
                                              ) and check

    if is_param(obj.input, 'e'):
        check = checker.check_datetime_string(_('End Date'),
                                              obj.input.e,
                                              CHECK_EMPTY | CHECK_VALID,
                                              obj.me.languages,
                                              ) and check

    if is_param(obj.input, 'st'):
        check = checker.check_time_string(_('Start Time'),
                                          obj.input.st,
                                          CHECK_EMPTY | CHECK_VALID,
                                          ) and check

    if is_param(obj.input, 'et'):
        check = checker.check_time_string(_('End Time'),
                                          obj.input.et,
                                          CHECK_EMPTY | CHECK_VALID,
                                          ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1LogBy1AppBy1(Rest):
    @auth
    def _GET(self, *param, **params):
        self.__template__.dir = "hostby1logby1appby1"
        self.__template__.file = "hostby1logby1appby1"
        self.__template__.media = "part"

        appname = param[1]
        filename = param[2]
        log_config = None

        if not validates_log(self):
            self.logger.debug("Get log failed. Did not validate.")
            return web.badrequest(self.view.alert)

        config = LogViewConfigParam(LOG_VIEW_XML_FILE)
        config.load_xml_config()
        app = config.findby1application(appname)

        for log in app['logs']:
            if log['filename'] == filename:
                log_config = log

        lines = []
        param_value = {}

        if is_param(self.input, 'k'):
            param_value["k"] = self.input.k
        else:
            param_value["k"] = ""

        start_day = str2datetime(self.input.s,
                                 DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0])
        end_day = str2datetime(self.input.e,
                                 DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][0])

        (start_hour, start_minute) = self.input.st.split(':', 2)
        (end_hour, end_minute) = self.input.et.split(':', 2)

        start_time = create_epochsec(start_day.year,
                                     start_day.month,
                                     start_day.day,
                                     int(start_hour),
                                     int(start_minute),
                                     )

        end_time = create_epochsec(end_day.year,
                                   end_day.month,
                                   end_day.day,
                                   int(end_hour),
                                   int(end_minute),
                                   )
        if int(start_time) > int(end_time):
            self.logger.error("Getting reports failed. Start time > end time.")
            return web.badrequest(_('Getting reports failed. Start time > end time.'))

        param_value["start_datetime"] = "%s %s" % (start_day.strftime("%Y/%m/%d"), self.input.st)
        param_value["end_datetime"] = "%s %s" % (end_day.strftime("%Y/%m/%d"), self.input.et)

        if log_config['view_lotatelog']:
            try:
                lines = read_log_with_lotate(filename,
                                             self.input.m,
                                             log_config,
                                             param_value["start_datetime"],
                                             param_value["end_datetime"],
                                             param_value["k"])
                if lines is False:
                    return web.notfound()
            except Exception, e:
                self.logger.warning("log file open error: %s" % e)
        else:
            log_dir = "/var/log/%s" % log_config['dir']
            try:
                lines = read_log("%s/%s" % (log_dir, log_config['filename']),
                                 self.input.m,
                                 log_config,
                                 param_value["statrt_datetime"],
                                 param_value["end_datetime"],
                                 param_value["k"])
                if lines is False:
                    return web.notfound()
            except Exception, e:
                self.logger.warning("log file open error: %s" % e)

        self.view.log_json = json_dumps(lines)
        return True

urls = ('/host/(\d+)/log/([0-9a-zA-Z\-]+)/([0-9a-zA-Z\-\.]+)$', HostBy1LogBy1AppBy1,)
