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

"""
@authors: Kazuya Hayashi <kazuya@karesansui-project.info>
"""

import os.path
from os import environ as env 

import web

from karesansui import KaresansuiGadgetException
from karesansui.lib.file.k2v import K2V
from karesansui.lib.rest import Rest, auth
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX, CHECK_LENGTH
from karesansui.lib.const import PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH
from karesansui.lib.utils import is_param

def validates_mail(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'server'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Mail Server Name'))
    else:
        check_server = checker.check_domainname(_('Mail Server Name'),
                        obj.input.server,
                        CHECK_EMPTY | CHECK_VALID,
                       ) or \
                       checker.check_ipaddr(_('Mail Server Name'),
                        obj.input.server,
                        CHECK_EMPTY | CHECK_VALID,
                       ) 
        check = check_server and check
    
    if not is_param(obj.input, 'port'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Port Number'))
    else:
        check = checker.check_number(_('Port Number'),
                    obj.input.port,
                    CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    PORT_MIN_NUMBER,
                    PORT_MAX_NUMBER,
                    ) and check
    
    if not is_param(obj.input, 'email'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Recipient Mail Address'))
    else:
        check = checker.check_mailaddress(_('Recipient Mail Address'),
                    obj.input.email,
                    CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                    min = EMAIL_MIN_LENGTH,
                    max = EMAIL_MAX_LENGTH
                    ) and check

    obj.view.alert = checker.errors
    return check

def get_view_mail(config):
    mail = {'server' : config['application.mail.server'],
            'port' : config['application.mail.port'],
            'email' : config['application.mail.email']}
    return mail

class Mail(Rest):
 
    @auth
    def _GET(self, *param, **params):
        try:
            conf = env.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            self.view.mail = get_view_mail(config)
            return True
        
        except IOError, kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge

    
    @auth
    def _PUT(self, *param, **params):
        if not validates_mail(self):
            return web.badrequest(self.view.alert)

        try:
            conf = env.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            config['application.mail.server'] = self.input.server
            config['application.mail.port'] = self.input.port
            config['application.mail.email'] = self.input.email
            _K2V.write(config)
            self.view.mail = get_view_mail(config)
            return True

        except IOError, kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge


urls = ('/setting/mail/?(\.input|\.part)?$', Mail,)
