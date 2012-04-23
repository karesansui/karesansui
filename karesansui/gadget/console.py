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

from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.merge import MergeGuest
from karesansui.lib.utils import get_xml_xpath as XMLXpath, get_xml_parse as XMLParse

from karesansui.db.access.machine import findbyguest1, findbyhost1
from karesansui.lib.const import KVM_BRIDGE_PREFIX

def _prep_console():
    java_dir = karesansui.dirname + '/static/java'
    source = '/usr/lib/tightvnc/classes/VncViewer.jar'
    target = java_dir + '/VncViewer.jar'

    if not os.path.lexists(target):
        if not os.path.exists(java_dir):
            os.makedirs(java_dir)
        os.symlink(source,target) 

class Console(Rest):

    @auth
    def _GET(self, *param, **params):
        _prep_console()

        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        model = findbyguest1(self.orm, guest_id)
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()

            dom = kvc.search_guests(domname)[0]

            document = XMLParse(dom.XMLDesc(1))

            self.view.graphics_port = XMLXpath(document,
                                          '/domain/devices/graphics/@port')
            self.view.xenname = XMLXpath(document,
                                         '/domain/name/text()')
        finally:
            kvc.close()

        h_model = findbyhost1(self.orm, host_id)
        try:
            from karesansui.lib.utils import get_ifconfig_info
            device = KVM_BRIDGE_PREFIX + "0"
            self.view.host_ipaddr = get_ifconfig_info(device)[device]["ipaddr"]
        except:
            try:
                self.view.host_ipaddr = h_model.hostname.split(":")[0].strip()
            except:
                self.view.host_ipaddr = socket.gethostbyname(socket.gethostname())

        return True

urls = (
    '/host/(\d+)/guest/(\d+)/console/?(\.part)$', Console,)
