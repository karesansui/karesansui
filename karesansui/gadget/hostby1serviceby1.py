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
from karesansui.lib.utils import is_param
from karesansui.lib.const import SERVICE_XML_FILE
from karesansui.lib.service.config import ServiceConfigParam
from karesansui.lib.service.sysvinit_rh import SysVInit_RH

class HostBy1ServiceBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()

        service = config.findby1service(param[1])
        if not service:
            self.logger.debug("Get service info failed. Service not found.")
            return web.notfound("Service not found")

        sysv = SysVInit_RH(service['system_name'], service['system_command'])
        display = {
            'name' : service['system_name'],
            'display_name' : service['display_name'],
            'description' : service['display_description'],
            'status' : sysv.status(),
            'autostart' : sysv.onboot(),
            }
        self.view.service = display

        return True

urls = (
    '/host/(\d+)/service/([a-zA-z\-]{4,32})/?(\.part)$', HostBy1ServiceBy1,
    )
