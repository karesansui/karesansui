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

from karesansui.lib.const import VIRT_COMMAND_SET_MAC_ADDRESS, \
                                 VIRT_COMMAND_DELETE_NIC
from karesansui.lib.virt.virt import KaresansuiVirtException, \
                                     KaresansuiVirtConnection
from karesansui.lib.merge import MergeGuest
from karesansui.lib.utils import is_int, is_param

from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

# validate

def validates_nicby1(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []
    
    # mac_address
    if is_param(obj.input, 'mac_address'):
        check = checker.check_macaddr(
            _('MAC Address'),
            obj.input.mac_address,
            CHECK_EMPTY | CHECK_VALID
            ) and check
    

    obj.view.alert = checker.errors

    return check

class GuestBy1NicBy1(Rest):
    
    @auth
    def _GET(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.notfound()       

        nic_id = int(param[2])

        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()

        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.notfound()
            virt = kvc.search_kvg_guests(domname)[0]
            
            guest = MergeGuest(model, virt)
            self.view.guest = guest
            if_info =  virt.get_interface_info()
            if len(if_info) <= nic_id:
                return web.notfound()

            self.view.nic_info = if_info[nic_id]
            
        finally:
            kvc.close()
            
        return True

    @auth
    def _PUT(self, *param, **params):

        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.notfound()       
        nic_id = int(param[2])


        if not validates_nicby1(self):
            return web.badrequest(self.view.alert)

        model = findbyguest1(self.orm, guest_id)
        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            guest = MergeGuest(model, virt)
            old_mac = virt.get_interface_info()[nic_id]['mac']['address']
            nic_info = virt.get_interface_info()
        finally:
            kvc.close()

        new_mac = self.input.mac_address

        if old_mac != new_mac:
            f_chk = True
            for x in nic_info:
                if x['mac']['address'] == new_mac:
                    f_chk = False
                    break
            if f_chk is False:
                return web.badrequest(_('Specified MAC address is already defined.'))

            self.logger.debug('spinning off change_mac_job dom=%s, from_mac=%s, to_mac=%s' % (domname, old_mac, new_mac))
            if change_mac_job(self, model, domname, old_mac, new_mac) is True:
                return web.accepted(url=web.ctx.path)
            else:
                return False

        else:
            return web.accepted(url=web.ctx.path)
            #return web.nocontent()

    @auth
    def _DELETE(self, *param, **params):
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if is_int(param[2]) is False:
            return web.notfound()       

        nic_id = int(param[2])

        model = findbyguest1(self.orm, guest_id)
        
        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            guest = MergeGuest(model, virt)
            nic_info = virt.get_interface_info()[nic_id]
        finally:
            kvc.close()

        mac = nic_info["mac"]["address"]
        self.logger.debug('spinning off delete_nic_job dom=%s, mac=%s' % (domname, mac))
        if delete_nic_job(self,model,domname,mac) is True:
            return web.accepted()
        else:
            return False
# -- lib
def change_mac_job(obj, guest, name, old_mac, new_mac, options={}):
    options['name'] = name
    options['from'] = old_mac
    options['to']   = new_mac

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_SET_MAC_ADDRESS), options)

    cmdname = u"Change MAC Address"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job("%s command" % cmdname, 0, _cmd))


    _machine2jobgroup = m2j_new(machine=guest,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )
    
    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )        
    return True

# -- lib
def delete_nic_job(obj, guest, name, mac, options={}):
    options['name'] = name
    options['mac']  = mac

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_NIC), options)

    cmdname = u"Delete NIC"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _jobgroup.jobs.append(Job("%s command" % cmdname, 0, _cmd))
    
    _machine2jobgroup = m2j_new(machine=guest,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )
    
    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )        
    return True
    #return web.accepted()
    
urls = (
    '/host/(\d+)/guest/(\d+)/nic/(\d+)/?(\.part|\.json)?$', GuestBy1NicBy1,
    )
