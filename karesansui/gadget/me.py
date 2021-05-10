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
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, \
    CHECK_CHAR, CHECK_MIN, CHECK_MAX, CHECK_ONLYSPACE
from karesansui.db.access.user import findby1, update as dba_update, findby1email
from karesansui.lib.crypt import sha1encrypt, sha1compare
from karesansui.lib.const import \
    DEFAULT_LANGS, LOGOUT_FILE_PREFIX, \
    ID_MIN_LENGTH, ID_MAX_LENGTH, \
    EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH, \
    USER_MIN_LENGTH, USER_MAX_LENGTH, \
    PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, \
    LANGUAGES_MIN_LENGTH, LANGUAGES_MAX_LENGTH
from karesansui.lib.utils import is_param, is_empty, create_file
from karesansui.gadget.userby1 import compare_password

def validates_me(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    _password_flag = True
    if not is_param(obj.input, 'password'):
        _password_flag = False
        check = False
        checker.add_error(_('"%s" is required.') % _('Password'))
    if not is_param(obj.input, 'new_password'):
        _password_flag = False
        check = False
        checker.add_error(_('"%s" is required.') % _('New Password'))
    if not is_param(obj.input, 'retype'):
        _password_flag = False
        check = False
        checker.add_error(_('"%s" is required.') % _('Retype'))

    if _password_flag == True:
        if not is_empty(obj.input.password) or \
           not is_empty(obj.input.new_password) or \
           not is_empty(obj.input.retype):
            check = checker.check_password(
                        _('Password'),
                        obj.input.password,
                        obj.input.password,
                        CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                        min = PASSWORD_MIN_LENGTH,
                        max = PASSWORD_MAX_LENGTH,
                        ) and check
            
            check = checker.check_password(
                        _('Password'),
                        obj.input.new_password,
                        obj.input.retype,
                        CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                        min = PASSWORD_MIN_LENGTH,
                        max = PASSWORD_MAX_LENGTH,
                        ) and check

    if not is_param(obj.input, 'id'):
        check = False
        checker.add_error(_('"%s" is required.') % _('ID'))
    else:
        check = checker.check_number(
                    _('ID'),
                    obj.input.id,
                    CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    min = ID_MIN_LENGTH,
                    max = ID_MAX_LENGTH,
                    ) and check

    if not is_param(obj.input, 'email'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Mail Address'))
    else:
        check = checker.check_mailaddress(
                    _('Mail Address'),
                    obj.input.email,
                    CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                    min = EMAIL_MIN_LENGTH,
                    max = EMAIL_MAX_LENGTH,
                    ) and check

    if not is_param(obj.input, 'nickname'):
        check = False
        checker.add_error(_('"%s" is required.') % _('User Name'))
    else:
        check = checker.check_username(
                    _('User Name'),
                    obj.input.nickname,
                    CHECK_EMPTY | CHECK_LENGTH | CHECK_ONLYSPACE,
                    min = USER_MIN_LENGTH,
                    max = USER_MAX_LENGTH,
                    ) and check

    if not is_param(obj.input, 'languages'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Language'))
    else:
        check = checker.check_languages(
                    _('Language'),
                    obj.input.languages,
                    CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                    min = LANGUAGES_MIN_LENGTH,
                    max = LANGUAGES_MAX_LENGTH,
                    ) and check

    obj.view.alert = checker.errors
    return check

class Me(Rest):
    @auth
    def _GET(self, *param, **params):
        if self.is_mode_input():
            self.view.locales = list(DEFAULT_LANGS.keys())
        return True

    @auth
    def _PUT(self, *param, **params):
        if not validates_me(self):
            return web.badrequest(self.view.alert)
        
        if self.me.id != int(self.input.id):
            self.logger.info("Update account is failed, "
                             "posted ID parameter is different from me ID "
                             "- posted ID %s, me ID %s" % (self.input.id, self.me.id))
            return web.badrequest(_('ID is wrong. Your ID is not %s.') % self.input.id)

        me = findby1(self.orm, self.input.id)
        if not me:
            self.logger.debug("Update account is failed, "
                              "Did not exist account - id=%s" % self.input.id)
            return web.notfound()

        cmp_user = findby1email(self.orm, self.input.email)
        if not cmp_user is None:
            if me.id != cmp_user.id:
                self.logger.info("Update account is failed, "
                                 "Already exists mail address "
                                 "- %s, %s" % (me, cmp_user))
                return web.conflict(web.ctx.path) 

        if self.input.password:
            if compare_password(self, self.me) is False:
                return web.badrequest(self.view.alert)
            (password, salt) = sha1encrypt(self.input.new_password)
            me.password = password
            me.salt = salt
        me.email = self.input.email
        me.languages = self.input.languages 
        me.nickname = self.input.nickname
        dba_update(self.orm, me)
        self.me = me
        return web.seeother(web.ctx.path)

    @auth
    def _DELETE(self, *param, **params):
        fname = '%s%s' % (LOGOUT_FILE_PREFIX, self.me.email,)

        try:
            create_file(fname, "")
        except IOError as ioe:
            self.logger.error("Logout failed, Failed to create logout file. - filename=%s" % fname)
            raise # return 500(Internal Server Error)

        return web.seeother('%s/logout' % web.ctx.home)

urls = ('/me/?(\.part)$', Me,)
 
