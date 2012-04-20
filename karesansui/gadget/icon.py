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
import os.path
import imghdr

import web

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_MIN, CHECK_MAX
from karesansui.lib.const import ICON_DIR_TPL
from karesansui.lib.utils import \
    create_file, remove_file, uniq_filename, is_param, is_path

def validates_icon(obj):
    checker = Checker()
    check = True
          
    _ = obj._ 
    checker.errors = []

    if is_param(obj.input, 'multi_icon'):
        check = checker.check_image(
                    _('Machine Icon'),
                    obj.input.multi_icon.value,
                    CHECK_EMPTY | CHECK_VALID,
                    None,
                    None,
            ) and check

    obj.view.alert = checker.errors
    return check

def add_prefix(msg, prefix):
    if isinstance(msg, str):
        msg = [msg]

    for i in xrange(len(msg)):
        msg[i] =  prefix + ":" + msg[i]
    return msg

class Icon(Rest):
    @auth
    def _POST(self, *param, **params):
        if not validates_icon(self):
            self.logger.debug("Create Icon is failed, Invalid input value")
            return web.badrequest(add_prefix(self.view.alert, "400"))

        icon_filevalue = self.input.multi_icon.value
        icon_filename = "%s.%s" % (uniq_filename(), imghdr.what(None, icon_filevalue))

        if is_path(icon_filename) is True:
            return web.badrequest("Not to include the path.")

        icon_realpath = ICON_DIR_TPL % (karesansui.dirname, icon_filename)
        icon_webpath = ICON_DIR_TPL % (web.ctx.homepath, icon_filename)

        if os.path.exists(icon_realpath):
            web.conflict(icon_webpath, add_prefix("icon already exists", "409"))

        try:
            create_file(icon_realpath, icon_filevalue)
        except IOError, ioe:
            self.logger.error("Failed to write icon file. - filename=%s" % icon_filename)
            return web.internalerror(add_prefix("Failed to create icon file.", "500"))

        return web.created(icon_webpath, icon_filename)

class IconBy1(Rest):
    @auth
    def _DELETE(self, *param, **params):
        icon_filename = param[0]
        if is_path(icon_filename) is True:
            return web.badrequest("Not to include the path.")

        icon_realpath = ICON_DIR_TPL % (karesansui.dirname, icon_filename)

        if not os.path.exists(icon_realpath):
            return web.notfound("icon not exists")

        try:
            remove_file(icon_realpath)
        except OSError, ose:
            self.logger.error("Failed to remove icon file. - filename=%s" % icon_filename)
            raise  # return 500(Internal Server Error)

        return web.seeother("/")

urls = (
    '/icon/(.+)/?$', IconBy1,
    '/icon/?$', Icon,
    )
