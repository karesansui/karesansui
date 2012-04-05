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

            self.view.vnc_port = XMLXpath(document,
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
