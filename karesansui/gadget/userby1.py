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
    LANGUAGES_MIN_LENGTH, LANGUAGES_MAX_LENGTH, \
    ID_MIN_LENGTH, ID_MAX_LENGTH

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
    if not is_param(obj.input, 'password'):
        check = False
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('Password'))
    if not is_param(obj.input, 'new_password'):
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('New Password'))
    if not is_param(obj.input, 'retype'):
        check = False
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('Retype'))

    if _password_flag == True:
        if not is_empty(obj.input.password) or \
           not is_empty(obj.input.new_password) or \
           not is_empty(obj.input.retype):
            check = checker.check_password(
                    _('Password'),
                    obj.input.password,
                    obj.input.password,
                    CHECK_EMPTY | CHECK_LENGTH,
                    min = PASSWORD_MIN_LENGTH,
                    max = PASSWORD_MAX_LENGTH,
                    ) and check

            check = checker.check_password(
                    _('Password'),
                    obj.input.new_password,
                    obj.input.retype,
                    CHECK_VALID | CHECK_LENGTH,
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

def validates_param_id(obj, user_id):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    check = checker.check_number(
            _('User ID'),
            user_id,
            CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
            min = ID_MIN_LENGTH,
            max = ID_MAX_LENGTH,
            ) and check

    obj.view.alert = checker.errors
    return check

def compare_password(obj, user):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not sha1compare(user.password, obj.input.password, user.salt):
        check = False
        checker.add_error(_('%s is mismatched.') % _('Current Password'))

    obj.view.alert = checker.errors
    return check

class UserBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        user_id = param[0]
        if not validates_param_id(self, user_id):
            self.logger.debug("Failed to update account. the value of parameter is invalid.")
            return web.notfound(self.view.alert)

        user = findby1(self.orm, user_id)
        if not user:
            self.logger.debug("Failed to get account - id=%s" % user_id)
            return web.notfound()
        self.view.user = user

        if self.is_mode_input():
            locales = list(DEFAULT_LANGS.keys())
            self.view.locales = locales
        return True

    @auth
    def _PUT(self, *param, **params):
        user_id = param[0]
        if not validates_param_id(self, user_id):
            self.logger.debug("Failed to update account. the value of parameter is invalid.")
            return web.notfound(self.view.alert)

        if not validates_user(self):
            self.logger.debug("Failed to update account. the value of input is invalid.")
            return web.badrequest(self.view.alert)

        user = findby1(self.orm, user_id)
        if not user:
            self.logger.debug("Failed to update account. No such account - id=%s" % user_id)
            return web.notfound()

        cmp_user = findby1email(self.orm, self.input.email)
        if not cmp_user is None:
            if int(user_id) != cmp_user.id:
                self.logger.debug("Failed to update account. The same mail address '%s' already exist - user='%s'" % (self.input.email, cmp_user.nickname))
                return web.conflict(web.ctx.path)

        user.nickname = self.input.nickname
        user.email = self.input.email
        user.languages = self.input.languages

        if not is_empty(self.input.new_password):
            if compare_password(self, user) == False:
                return web.badrequest(self.view.alert)

            (password, salt) = sha1encrypt(self.input.new_password)
            user.password = password
            user.salt = salt

        update(self.orm, user)
        return web.seeother(web.ctx.path)

    @auth
    def _DELETE(self, *param, **params):
        user_id = param[0]
        if not validates_param_id(self, user_id):
            self.logger.debug("Failed to delete account. the value of parameter is invalid.")
            return web.notfound(self.view.alert)

        user = findby1(self.orm, user_id)
        if not user:
            self.logger.debug("Failed to delete account. No such account - id=%s" % user_id)
            return web.notfound()

        users = findbyall(self.orm)

        if len(users) <= 1:
            self.view.alert = "In case that Karesansui has one account only, It does not allow to delete account."
            return web.badrequest(self.view.alert)

        delete(self.orm, user)
        return web.seeother("/%s.%s" % ("user", "part"))

urls = (
    '/user/(\d+)/?(\.part)$', UserBy1,
    )
