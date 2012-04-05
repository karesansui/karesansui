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
from karesansui.lib.file.k2v import K2V
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

    if not is_param(obj.input, 'hostname'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Server Name'))
    else:
        check_server = checker.check_domainname(_('Server Name'),
                        obj.input.hostname,
                        CHECK_VALID,
                       ) or \
                       checker.check_ipaddr(_('Server Name'),
                        obj.input.hostname,
                        CHECK_VALID,
                       )
        check = check_server and check

    if not is_param(obj.input, 'port'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Port Number'))
    else:
        check = checker.check_number(_('Port Number'),
                    obj.input.port,
                    CHECK_VALID | CHECK_MIN | CHECK_MAX,
                    PORT_MIN_NUMBER,
                    PORT_MAX_NUMBER,
                    ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1SettingBy1Mail(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            self.view.config = config
        except (IOError, KaresansuiGadgetException), kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge

        if self.is_mode_input() is True:
            pass

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_mail(self):
            self.logger.debug("Update mail setting failed. Did not validate.")
            return web.badrequest(self.view.alert)

        hostname = self.input.hostname
        port     = self.input.port
        if not port:
            port = "25"

        if hostname:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            try:
                sock.connect((hostname, int(port)))
            except Exception, e:
                self.logger.error("Could not connect to specified MTA \n%s" % e)
                """
                TRANSLATORS:
                MTA設定の際に実際に指定したホスト名/ポート番号に接続ができる
                かチェックし、接続できなかった。
                """
                return web.badrequest(_("Could not connect to specified MTA \n%s" % e))

        try:
            conf = os.environ.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
            config['application.mail.server'] = hostname
            config['application.mail.port'] = port
            _K2V.write(config)
            self.view.config = config
            return True

        except IOError, kge:
            self.logger.debug(kge)
            raise KaresansuiGadgetException, kge

urls = ('/host/(\d+)/setting/mail?(\.input|\.part)$', HostBy1SettingBy1Mail,)
