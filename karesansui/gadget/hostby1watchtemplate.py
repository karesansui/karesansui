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

from karesansui.lib.rest import Rest, auth
from karesansui.lib.utils import read_file, json_dumps
from karesansui.lib.const import TEMPLATE_DIR, \
    MAIL_TEMPLATE_COLLECTD_WARNING, \
    MAIL_TEMPLATE_COLLECTD_FAILURE, \
    MAIL_TEMPLATE_COLLECTD_OKAY, \
    WATCH_PLUGINS, DEFAULT_LANGS

from karesansui.lib.checker import Checker

def validates_watch(obj, target, lang):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    if target not in WATCH_PLUGINS.values():
        check = False
        checker.add_error(_('"%s" is not watch target.') %_(target))

    if lang not in DEFAULT_LANGS:
        check = False
        checker.add_error(_('"%s" is not supported language.') %_(lang))

    obj.view.alert = checker.errors
    return check

class HostBy1WatchTemplate(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        target = param[1]
        if target is None: return web.notfound()

        lang = param[2]
        if lang is None: return web.notfound()

        if not validates_watch(self, target, lang):
            self.logger.debug("Get watch mail template failed. Did not validate.")
            return web.badrequest(self.view.alert)

        template_dir = "%s/%s" % (TEMPLATE_DIR,lang[0:2],)

        mail_template_warning = read_file("%s/%s" % (template_dir,MAIL_TEMPLATE_COLLECTD_WARNING[target]))
        mail_template_failure = read_file("%s/%s" % (template_dir,MAIL_TEMPLATE_COLLECTD_FAILURE[target]))
        mail_template_okay = read_file("%s/%s" % (template_dir,MAIL_TEMPLATE_COLLECTD_OKAY[target]))

        data = {
            "mail_template_warning" : mail_template_warning,
            "mail_template_failure" : mail_template_failure,
            "mail_template_okay" : mail_template_okay,
            }

        self.view.data = json_dumps(data)
        return True

urls = (
    '/host/(\d+)/watch/([a-zA-Z0-9]+)/([a-z]{2}|[a-z]{2}_[A-Z]{2})?(\.json)$', HostBy1WatchTemplate,
    )
