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

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.const import VIRT_COMMAND_SET_VNC, \
     VNC_PORT_MIN_NUMBER, VNC_PORT_MAX_NUMBER
from karesansui.lib.const import XEN_KEYMAP_DIR, KVM_KEYMAP_DIR

from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection
from karesansui.lib.utils import is_int, is_param, get_keymaps
from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX, CHECK_EXIST

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access.machine import findbyguest1
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command


def validates_display(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'port'):
        check = False
        checker.add_error(_('"%s" is required.') % _('VNC Port Number'))
    else:
        check = checker.check_number(
                _('VNC Port Number'),
                obj.input.port,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                min = VNC_PORT_MIN_NUMBER,
                max = VNC_PORT_MAX_NUMBER,
            ) and check

    if not is_param(obj.input, 'listen'):
        check = False
        checker.add_error(_('"%s" is required.') % _('VNC listen address'))
    else:
        check = checker.check_empty(
                _('VNC listen address'), 
                obj.input.listen
            ) and check

        if check is True:
            if not obj.input.listen in ["0.0.0.0", "127.0.0.1"]:
                checker.add_error(_('%s is in invalid format.') % (_('VNC listen address')))
                check = False
            else:
                check = True

    if not is_param(obj.input, 'change_passwd'):
        check = False
        checker.add_error(_('"%s" is required.') % _('VNC Password'))
    else:
        check = checker.check_empty(
                _('VNC Password'), 
                obj.input.change_passwd
            ) and check

        if check is True:
            if not obj.input.change_passwd in ["random", "empty", "keep"]:
                checker.add_error(_('%s is in invalid format.') % (_('VNC Password')))
                check = False
            else:
                check = True

    hypervisor = "KVM"
    if obj.input.VMType == 'XEN':
        hypervisor = "XEN"
    elif obj.input.VMType == 'KVM':
        hypervisor = "KVM"

    if not is_param(obj.input, 'keymap'):
        check = False
        checker.add_error(_('"%s" is required.') % _('VNC Keymap'))
    else:
        check = checker.check_keymap(
                _('VNC Keymap'),
                obj.input.keymap,
                CHECK_EMPTY | CHECK_EXIST,
                hypervisor) and check

    obj.view.alert = checker.errors
    return check
    

class GuestBy1Display(Rest):

    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()
            virt = kvc.search_kvg_guests(domname)[0]

            info = virt.get_graphics_info()
            self.view.checked_listen_all = ""
            self.view.checked_listen_lo = "checked"
            try:
                if info["setting"]["listen"] == "0.0.0.0":
                    self.view.checked_listen_all = "checked"
                    self.view.checked_listen_lo = ""
            except:
                pass

            self.view.VMType = virt.get_info()['VMType']
            self.view.keymaps = eval("get_keymaps(%s_KEYMAP_DIR)" % self.view.VMType.upper())
            self.view.info = info
            self.view.guest = model

        finally:
            kvc.close()
            
        return True


    @auth
    def _PUT(self, *param, **params):
        """<comment-ja>
        Japanese Comment
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if not validates_display(self):
            return web.badrequest(self.view.alert)

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            info = virt.get_graphics_info()["setting"]

            used_ports = kvc.list_used_vnc_port()
            origin_port = info["port"]

        finally:
            kvc.close()

        options = {}
        options["name"] = domname
        if self.input.change_passwd == "random":
            options["random-passwd"] = None
        elif self.input.change_passwd == "empty":
            options["passwd"] = ""
        options["port"] = self.input.port
        options["listen"] = self.input.listen
        options["keymap"] = self.input.keymap

        if int(self.input.port) != origin_port and int(self.input.port) in used_ports:
            return web.badrequest("VNC port number has been already used by other service. - port=%s" % (self.input.port,))

        _cmd = dict2command("%s/%s" % (karesansui.config['application.bin.dir'],
                                       VIRT_COMMAND_SET_VNC),
                            options)

        cmdname = "Set VNC"
        _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('%s command' % cmdname, 0, _cmd))
        
        _machine2jobgroup = m2j_new(machine=model,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )
        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               _jobgroup,
                               )
        return web.created(None)
            

urls = ('/host/(\d+)/guest/(\d+)/display/?(\.part)$', GuestBy1Display,)
