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
@authors: Hiroki Takayasu <hiroki@karesansui-project.info>
"""
import os
import web
import socket

from karesansui.lib.rest import Rest, auth
from karesansui.lib.file.k2v import K2V
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, \
    CHECK_MIN, CHECK_MAX, CHECK_LENGTH, \
    CHECK_ONLYSPACE
from karesansui.lib.const import PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH, \
    PROXY_ENABLE, PROXY_DISABLE
from karesansui.lib.utils import is_param
from karesansui import KaresansuiGadgetException, KaresansuiDBException, \
    config, sheconf

def validates_proxy(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'proxy_status'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Proxy Settings'))
    else:
        if obj.input.proxy_status == PROXY_ENABLE:
            if not is_param(obj.input, 'proxy_server'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Proxy Server'))
            else:
                check = checker.check_domainname(
                                _('Proxy Server'),
                                obj.input.proxy_server,
                                CHECK_EMPTY | CHECK_VALID,
                                None,
                                None,
                                ) and check
            if not is_param(obj.input, 'proxy_port'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Proxy Port Number'))
            else:
                check = checker.check_number(
                                _('Port Number'),
                                obj.input.proxy_port,
                                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                PORT_MIN_NUMBER,
                                PORT_MAX_NUMBER,
                                ) and check
            if not is_param(obj.input, 'proxy_user'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Proxy User Name'))
            else:
                check = checker.check_username(
                                _('Proxy User Name'),
                                obj.input.proxy_user,
                                CHECK_VALID | CHECK_ONLYSPACE,
                                None,
                                None,
                                ) and check
            if not is_param(obj.input, 'proxy_password'):
                check = False
                checker.add_error(_('"%s" is required.') % _('Proxy Password'))
            else:
                check = checker.check_password(
                                _('Proxy Password'),
                                obj.input.proxy_password,
                                obj.input.proxy_password,
                                CHECK_VALID,
                            ) and check;

        elif obj.input.proxy_status == PROXY_DISABLE:
            check = True and check
        else:
            check = False
            checker.add_error(_('"%s" is in invalid format.') % _('Proxy Status'))

    obj.view.alert = checker.errors
    return check

class HostBy1SettingBy1Proxy(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            self.view.config = config
        except (IOError, KaresansuiGadgetException) as kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException(kge)

        if self.is_mode_input() is True:
            self.view.enable = ""
            self.view.disable = ""
            if config['application.proxy.status'] == PROXY_ENABLE:
                self.view.enable = "checked"
            else:
                self.view.disable = "checked"

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_proxy(self):
            self.logger.debug("Update proxy setting failed. Did not validate.")
            return web.badrequest(self.view.alert)

        if self.input.proxy_status == PROXY_ENABLE:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            try:
                sock.connect((self.input.proxy_server, int(self.input.proxy_port)))
            except Exception as e:
                self.logger.error("Could not connect to specified proxy server\n%s" % e)
                """
                TRANSLATORS:
                プロキシ設定の際に実際に指定したプロキシのホスト名/ポート番号
                に接続ができるかチェックし、接続できなかった。
                """
                return web.badrequest(_("Could not connect to specified proxy server\n%s" % e))

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()

            config['application.proxy.status'] = self.input.proxy_status
            if self.input.proxy_status == PROXY_ENABLE:
                config['application.proxy.server'] = self.input.proxy_server
                config['application.proxy.port'] = self.input.proxy_port
                config['application.proxy.user'] = self.input.proxy_user
                config['application.proxy.password'] = self.input.proxy_password
            _K2V.write(config)
        except (IOError, KaresansuiGadgetException) as kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException(kge)
        return web.accepted(url=web.ctx.path)

urls = ('/host/(\d+)/setting/proxy?(\.input|\.part)$', HostBy1SettingBy1Proxy,)
