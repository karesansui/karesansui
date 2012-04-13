# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
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
from karesansui.lib.pager import Pager, validates_page
from karesansui.lib.search import validates_query
from karesansui.lib.const import \
    TAG_LIST_RANGE, TAG_MIN_LENGTH, TAG_MAX_LENGTH, \
    ID_MIN_LENGTH, ID_MAX_LENGTH

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, \
    CHECK_LENGTH, CHECK_MIN, CHECK_MAX

from karesansui.db.access.tag import \
    findbyall, findby1, \
    findby1name, findbyand,\
    update, delete, save, new
from karesansui.lib.utils import is_param

def validates_tag(obj):
    checker = Checker()
    check = True
          
    _ = obj._ 
    checker.errors = []

    check = check and checker.check_length(
            _('Tag'),
            obj.input.name,
            TAG_MIN_LENGTH,
            TAG_MAX_LENGTH,
            ) 

    obj.view.alert = checker.errors
    return check

def validates_param_id(obj, tag_id):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    check = checker.check_number(
            _('Tag ID'),
            tag_id,
            CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
            min = ID_MIN_LENGTH,
            max = ID_MAX_LENGTH,
            ) and check

    obj.view.alert = checker.errors
    return check

class Tag(Rest):
    @auth
    def _GET(self, *param, **params):
        if not validates_query(self):
            self.logger.debug("Failed to get tags. The value of query is invalid.")
            return web.badrequest(self.view.alert)

        if not validates_page(self):
            self.logger.debug("Failed to get tags. The value of page is invalid.")
            return web.badrequest(self.view.alert)

        if is_param(self.input, 'q') is True:
            tags = findbyand(self.orm, self.input.q)
            if not tags:
                self.logger.debug("Failed to get tags. No such tag - query=%s" % self.input.q)
                return web.nocontent()
            self.view.search_value = self.input.q
        else:
            tags = findbyall(self.orm)
            self.view.search_value = ""
            if not tags:
                self.logger.debug("Failed to get tag. No tags found.")
                return web.notfound()

        if is_param(self.input, 'p') is True:
            start = int(self.input.p)
        else:
            start = 0

        pager = Pager(tags, start, TAG_LIST_RANGE)
        if not pager.exist_now_page():
            self.logger.debug("Failed to get tag. Could not find page - page=%s" % self.input.p)
            return web.nocontent()

        self.view.pager = pager

        if self.is_mode_input():
            self.view.tag = new('')

        self.view.input = self.input
        return True

    @auth
    def _POST(self, *param, **params):
        if not validates_tag(self):
            self.logger.debug("Failed to create tag. The value of input is invalid.")
            return web.badrequest(self.view.alert)

        tag = findby1name(self.orm, self.input.name)
        if tag:
            self.logger.debug("Failed to create tag. The same tag already exist - id='%s'" % (tag.id))
            return web.conflict(web.ctx.path)

        new_tag = new(self.input.name)

        save(self.orm, new_tag)
        return web.created(None)


class TagBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        tag_id = param[0]
        if not validates_param_id(self, tag_id):
            self.logger.debug("Failed to get tag. The value of parameter is invalid.")
            return web.badrequest(self.view.alert)

        tag = findby1(self.orm, tag_id)
        if not tag:
            self.logger.debug("Failed to get tag. No such tag - id=%s" % tag_id)
            return web.notfound()
        self.view.tag = tag
        
        return True

    @auth
    def _PUT(self, *param, **params):
        tag_id = param[0]
        if not validates_param_id(self, tag_id):
            self.logger.debug("Failed to update tag. The value of parameter is invalid.")
            return web.badrequest(self.view.alert)

        if not validates_tag(self):
            self.logger.debug("Failed to update tag. The value of input is invalid.")
            return web.badrequest(self.view.alert)

        tag = findby1(self.orm, tag_id)
        if not tag:
            self.logger.debug("Failed to update tag. No such tag - id=%s" % tag_id)
            return web.notfound() 

        cmp_tag = findby1name(self.orm, self.input.name)
        if not cmp_tag is None:
            if cmp_tag.id != tag.id:
                self.logger.debug("Failed to update tag. The same tag already exist - id='%s'" % (cmp_tag.id))
                return web.conflict(web.ctx.path)

        tag.name = self.input.name

        update(self.orm, tag)
        return web.seeother(web.ctx.path)

    @auth
    def _DELETE(self, *param, **params):
        tag_id = param[0]
        if not validates_param_id(self, tag_id):
            self.logger.debug("Failed to delete tag. The value of parameter is invalid.")
            return web.badrequest(self.view.alert)

        tag = findby1(self.orm, tag_id)
        if not tag:
            self.logger.debug("Failed to delete tag. No such tag - id=%s" % tag_id)
            return web.notfound() 

        delete(self.orm, tag)
        return web.seeother("/%s.%s" % ("tag", "part"))

urls = (
    '/tag/(\d+)/?(\.part)$', TagBy1,
    '/tag/?(\.part)$', Tag,
    )
