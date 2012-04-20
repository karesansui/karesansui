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

from karesansui.db.access.user import \
    findbyall, findby1, findby1email, findbyand, \
    update, delete, save, new

from karesansui.lib.crypt import sha1encrypt, sha1compare
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_CHAR, CHECK_MIN, CHECK_MAX, CHECK_ONLYSPACE
from karesansui.lib.const import \
    DEFAULT_LANGS, USER_LIST_RANGE, \
    EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH, \
    USER_MIN_LENGTH, USER_MAX_LENGTH, \
    EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH, \
    PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, \
    LANGUAGES_MIN_LENGTH, LANGUAGES_MAX_LENGTH

from karesansui.lib.pager import Pager, validates_page
from karesansui.lib.search import validates_query
from karesansui.lib.utils import is_param, is_empty

def validates_user(obj):
    checker = Checker()
    check = True
          
    _ = obj._ 
    checker.errors = []

    if not is_param(obj.input, 'nickname'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Nickname'))
    else:
        check = checker.check_username(
                _('Nickname'),
                obj.input.nickname,
                CHECK_EMPTY | CHECK_LENGTH | CHECK_ONLYSPACE,
                min = USER_MIN_LENGTH,
                max = USER_MAX_LENGTH,
                ) and check

    if not is_param(obj.input, 'email'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Mail Address'))
    else:
        check = checker.check_mailaddress(
                _('Mail Address'), 
                obj.input.email,
                CHECK_EMPTY | CHECK_LENGTH | CHECK_VALID,
                min = EMAIL_MIN_LENGTH,
                max = EMAIL_MAX_LENGTH,
                ) and check 
    
    _password_flag = True
    if not is_param(obj.input, 'new_password'):
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('New Password'))
    if not is_param(obj.input, 'retype'):
        check = False
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('Retype'))

    if _password_flag == True:
        check = checker.check_password(
                _('Password'),
                obj.input.new_password,
                obj.input.retype,
                CHECK_VALID | CHECK_LENGTH | CHECK_EMPTY,
                min = PASSWORD_MIN_LENGTH,
                max = PASSWORD_MAX_LENGTH,
                ) and check

    check = checker.check_languages(
            _('Language'),
            obj.input.languages,
            CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
            min = LANGUAGES_MIN_LENGTH,
            max = LANGUAGES_MAX_LENGTH,
            ) and check

    obj.view.alert = checker.errors
    return check

class User(Rest):
    @auth
    def _GET(self, *param, **params):
        if not validates_query(self):
            self.logger.debug("Failed to get account. the value of query is invalid. - query=%s" % self.input.q)
            return web.badrequest(self.view.alert)

        if not validates_page(self):
            self.logger.debug("Failed to get account. the value of page is invalid. - page=%s" % self.input.p)
            return web.badrequest(self.view.alert)

        if is_param(self.input, "q"):
            users = findbyand(self.orm, self.input.q)
            if not users:
                self.logger.debug("Failed to get account. No such account. - query=%s" % self.input.q)
                return web.nocontent()
            self.view.search_value = self.input.q
        else:
            users = findbyall(self.orm)
            self.view.search_value = ""
            if not users:
                self.logger.debug("Failed to get account. No accounts found.")
                return web.notfound()

        if is_param(self.input, "p"):
            start = int(self.input.p)
        else:
            start = 0

        pager = Pager(users, start, USER_LIST_RANGE)
        if not pager.exist_now_page():
            self.logger.debug("Failed to get account. Could not find page - page=%s" % self.input.p)
            return web.nocontent()

        self.view.pager = pager

        if self.is_mode_input():
            locales = DEFAULT_LANGS.keys()
            self.view.locales = locales
            self.view.user = new('', '', '', '', '')

        self.view.input = self.input
        return True

    @auth
    def _POST(self, *param, **params):
        if not validates_user(self):
            self.logger.debug("Failed to create account. the values of input are invalid.")
            return web.badrequest(self.view.alert)

        user = findby1email(self.orm, self.input.email)
        if user:
            self.logger.debug("Failed to create account. The same mail address '%s' already exist - user='%s'" % (self.input.email, user.nickname))
            return web.conflict(web.ctx.path)

        (password, salt) = sha1encrypt(self.input.new_password)

        new_user = new(self.input.email,
                       password,
                       salt,
                       self.input.nickname,
                       self.input.languages
                       )

        save(self.orm, new_user)
        return web.created(None)

urls = (
    '/user/?(\.part)$', User,
    )
