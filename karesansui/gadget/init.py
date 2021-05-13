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

import socket
import karesansui
import web
from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import is_uuid, is_int, karesansui_database_exists
from karesansui.lib.utils import generate_phrase, generate_uuid, string_from_uuid

from karesansui.lib.file.k2v import K2V
from karesansui.lib.crypt import sha1encrypt, sha1compare
from karesansui.lib.const import MACHINE_ATTRIBUTE, MACHINE_HYPERVISOR
from karesansui.db import get_engine, get_metadata, get_session
from karesansui.db.model.user import User
from karesansui.db.model.notebook import Notebook
from karesansui.db.model.tag import Tag
from karesansui.db.model.machine import Machine

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

from karesansui.lib.utils import is_param, is_empty

def validates_user(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

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
    if not is_param(obj.input, 'retype'):
        check = False
        _password_flag = False
        checker.add_error(_('"%s" is required.') % _('Retype'))

    if _password_flag == True:
        if not is_empty(obj.input.password) or \
           not is_empty(obj.input.retype):
            check = checker.check_password(
                    _('Password'),
                    obj.input.password,
                    obj.input.password,
                    CHECK_EMPTY | CHECK_LENGTH,
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

class Init(Rest):

    def _GET(self, *param, **params):

        self.view.database_bind = karesansui.config['database.bind'] 
        self.view.default_locale = karesansui.config['application.default.locale'] 
        self.view.locales = list(DEFAULT_LANGS.keys())

        if karesansui_database_exists() is True:
            return web.tempredirect("/", absolute=False)

        if self.is_mode_input():
            return True
        else:
            return True
 
        return True

    def _POST(self, *param, **params):

        if not validates_user(self):
            return web.badrequest(self.view.alert)

        engine = get_engine()
        metadata = get_metadata()
        session = get_session()

        try:
            metadata.drop_all()   
            metadata.tables['machine2jobgroup'].create()
            metadata.create_all()   
        except Exception as e:
            traceback.format_exc()
            raise Exception('Initializing/Updating a database error - %s' % ''.join(e.args))

        (password, salt) = sha1encrypt(self.input.password)

        user  = User("%s" % self.input.email,
                              str(password),
                              str(salt),
                              "%s" % self.input.nickname,
                              "%s" % self.input.languages,
                              )
        session.add(user)
        session.commit()

        # Tag Table set.
        tag = Tag("default")
        session.add(tag)
        session.commit()
        
        # Machine Table set.
        #user = session.query(User).filter(User.email == self.input.email).first()
        uuid = string_from_uuid(generate_uuid())
        fqdn = socket.gethostname() 
        notebook = Notebook("", "")
        machine  = Machine(user,
                       user,
                       "%s" % uuid,
                       "%s" % fqdn,
                       MACHINE_ATTRIBUTE['HOST'],
                       MACHINE_HYPERVISOR['REAL'],
                       notebook,
                       [tag],
                       "%s" % fqdn,
                       'icon-guest1.png',
                       False,
                       None,
                      )
        session.add(machine)
        session.commit()

        session.close()

        return web.created(None)

urls = ('/init/?(\.part)?$', Init,)
