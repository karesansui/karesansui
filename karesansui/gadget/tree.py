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

        from karesansui.lib.file.configfile import LighttpdPortConf
        from karesansui.lib.const import LIGHTTPD_PORT_CONFIG
        try:
            conf_file = config['lighttpd.etc.dir'] + '/' + LIGHTTPD_PORT_CONFIG
            port_number = int(LighttpdPortConf(conf_file).read())
        except:
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
            self.kvc.close()
            raise KaresansuiGadgetException

        return True

urls = (
    '/tree/?(\.part)$' , Tree,
)
