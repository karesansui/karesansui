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

from os import environ as env

import web

from karesansui import KaresansuiGadgetException
from karesansui.lib.rest import Rest, auth
from karesansui.lib.net.http import is_ssl
from karesansui.lib.file.k2v import K2V
from karesansui.lib.virt.virt import KaresansuiVirtConnection, \
     KaresansuiVirtException
from karesansui.lib.merge import MergeHost
from karesansui.db.access.machine import findbyhostall
from karesansui.lib.utils import available_virt_uris

class Tree(Rest):

    def _post(self, f):
        ret = Rest._post(self, f)
        if hasattr(self, "kvc") is True:
            self.kvc.close()
        return ret

    @auth
    def _GET(self, *param, **params):
        models = findbyhostall(self.orm)
        uris = available_virt_uris()

        try:
            conf = env.get('KARESANSUI_CONF')
            _K2V = K2V(conf)
            config = _K2V.read()
        except (IOError, KaresansuiGadgetException):
            raise KaresansuiGadgetException

        self.view.application_uniqkey = config['application.uniqkey']

        port_number = 443

        try:
            hosts = []
            for model in models:
                if model.attribute == 0 and model.hypervisor == 1:
                    uri = uris["XEN"]
                elif model.attribute == 0 and model.hypervisor == 2:
                    uri = uris["KVM"]
                else:
                    uri = None
                self.kvc = KaresansuiVirtConnection(uri)
                host = MergeHost(self.kvc, model)
                host.info['model'].is_ssl = is_ssl(host.info['model'].hostname)
                #host.info['model'].is_ssl = is_ssl(host.info['model'].hostname,port_number)
                host.info['model'].port_number = port_number
                hosts.append(host)

            self.view.machines = hosts
        except KaresansuiVirtException:
            if hasattr(self, "kvc") is True:
                self.kvc.close()
            raise KaresansuiGadgetException

        return True

urls = (
    '/tree/?(\.part)$' , Tree,
)
