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
