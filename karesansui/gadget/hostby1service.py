# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import web

from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import SERVICE_XML_FILE
from karesansui.lib.service.config import ServiceConfigParam, ServiceXMLGenerator
from karesansui.lib.service.sysvinit_rh import SysVInit_RH

class HostBy1Service(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()

        displays = []
        for service in config.get_services():
            sysv = SysVInit_RH(service['system_name'], service['system_command'])
            display = {
                'name' : service['system_name'],
                'readonly': service['system_readonly'],
                'display_name' : service['display_name'],
                'description' : service['display_description'],
                'status' : sysv.status(),
                'autostart' : sysv.onboot(),
                }

            displays.append(display)

            self.view.services = displays

        return True

urls = (
    '/host/(\d+)/service/?(\.part)$', HostBy1Service,
    )
