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
from karesansui.lib.log.config import LogViewConfigParam
from karesansui.lib.const import LOG_VIEW_XML_FILE

class HostBy1Log(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()
        self.view.host_id = host_id

        config = LogViewConfigParam(LOG_VIEW_XML_FILE)
        config.load_xml_config()
        self.view.apps = config.get_applications()
        return True

urls = ('/host/(\d+)/log?(\.part)$', HostBy1Log,)
