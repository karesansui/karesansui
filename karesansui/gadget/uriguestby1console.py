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
import os
import socket

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.db.access.machine import findbyhost1
from karesansui.lib.utils import uri_split, uri_join

def _prep_console():
    java_dir = karesansui.dirname + '/static/java'

    sources = ['/usr/lib/tightvnc/classes/VncViewer.jar',
               '/usr/share/tightvnc-java/VncViewer.jar',
              ]

    target = java_dir + '/VncViewer.jar'

    if not os.path.lexists(target):
        if not os.path.exists(java_dir):
            os.makedirs(java_dir)

        for source in sources:
          if os.path.exists(source):
            os.symlink(source,target) 

class UriGuestBy1Console(Rest):

    @auth
    def _GET(self, *param, **params):
        _prep_console()

        host_id =  param[0]
        host_id = self.chk_hostby1(param)
        if host_id is None:
            return web.notfound()

        uri_id =  param[1]
        if uri_id is None:
            return web.notfound()

        model = findbyhost1(self.orm, host_id)
        try:
            segs = uri_split(model.hostname)
            self.view.host_ipaddr = socket.gethostbyname(segs['host'])
#172.23.227.50
        except:
            self.view.host_ipaddr = socket.gethostbyname(socket.gethostname())

        return True

urls = (
    '/host/(\d+)/uriguest/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/console/?(\.part)?$', UriGuestBy1Console,
    )
