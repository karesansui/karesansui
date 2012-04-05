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

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection, KaresansuiVirtGuest
from karesansui.lib.const import VIRT_COMMAND_START_GUEST, \
     VIRT_COMMAND_SHUTDOWN_GUEST, VIRT_COMMAND_SUSPEND_GUEST, \
     VIRT_COMMAND_RESUME_GUEST, VIRT_COMMAND_REBOOT_GUEST, \
     VIRT_COMMAND_DESTROY_GUEST, VIRT_COMMAND_AUTOSTART_GUEST
from karesansui.lib.utils import json_dumps, is_param
from karesansui.lib.checker import \
    Checker, CHECK_EMPTY, CHECK_VALID

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration

from pysilhouette.command import dict2command 
from karesansui.db.model._2pysilhouette import Job, JobGroup

GUEST_ACTION_CREATE = 0
GUEST_ACTION_SHUTDOWN = 1
GUEST_ACTION_DESTROY = 2
GUEST_ACTION_SUSPEND = 3
GUEST_ACTION_RESUME = 4
GUEST_ACTION_REBOOT = 5
GUEST_ACTION_ENABLE_AUTOSTART = 6
GUEST_ACTION_DISABLE_AUTOSTART = 7

def validates_guest_status(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'status'):
        check = checker.check_status(
                _('Status'),
                obj.input.status,
                CHECK_EMPTY | CHECK_VALID,
                [GUEST_ACTION_CREATE, 
                GUEST_ACTION_SHUTDOWN,
                GUEST_ACTION_DESTROY,
                GUEST_ACTION_SUSPEND,
                GUEST_ACTION_RESUME,
                GUEST_ACTION_REBOOT,
                GUEST_ACTION_ENABLE_AUTOSTART,
                GUEST_ACTION_DISABLE_AUTOSTART]
            ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Status'))

    obj.view.alert = checker.errors

    return check


class GuestBy1Status(Rest):
    
    @auth
    def _GET(self, *param, **params):
        """<comment-ja>
        virDomainState
         - VIR_DOMAIN_NOSTATE = 0
         - VIR_DOMAIN_RUNNING = 1
         - VIR_DOMAIN_BLOCKED = 2
         - VIR_DOMAIN_PAUSED = 3
         - VIR_DOMAIN_SHUTDOWN = 4
         - VIR_DOMAIN_SHUTOFF = 5
         - VIR_DOMAIN_CRASHED = 6
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()
        
        model = findbyguest1(self.orm, guest_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)
            
            if self.__template__["media"] == 'json':
                self.view.status = json_dumps(virt[0].status())
            else:
                self.view.status = virt[0].status()
                
        finally:
            kvc.close()

        #self.__template__.dir = 'guestby1'
        return True

    @auth
    def _PUT(self, *param, **params):
        """<comment-ja>
        ステータス更新
         - param
           - create = 0
           - shutdown = 1
           - destroy = 2
           - suspend = 3
           - resume = 4
           - reboot = 5
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        (host_id, guest_id) = self.chk_guestby1(param)
        if guest_id is None: return web.notfound()

        if not validates_guest_status(self):
            return web.badrequest(self.view.alert)

        status = int(self.input.status)

        model = findbyguest1(self.orm, guest_id)
        
        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)

            if status == GUEST_ACTION_CREATE:
                # -- Create
                cmdname = ["Start Guest", "start guest"]
                if virt[0].is_creatable() is True:
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_START_GUEST),
                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_START_GUEST
                else:
                    self.logger.error("Create Action:The state can not run. - %d" % virt[0].status())
                
            elif status == GUEST_ACTION_SHUTDOWN:
                cmdname = ["Shutdown Guest", "shutdown guest"]
                if virt[0].is_shutdownable() is True:
                    # -- Shutdown
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_SHUTDOWN_GUEST),
                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_SHUTDOWN_GUEST
                else:
                    self.logger.error("Shutdown Action:The state can not run. - %d" % virt[0].status())
            
            elif status == GUEST_ACTION_DESTROY:
                cmdname = ["Destroy Guest", "Destroy guest"]
                if virt[0].is_destroyable() is True:
                    # -- destroy
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_DESTROY_GUEST),
                                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_DESTROY_GUEST
                else:
                    self.logger.error("Destroy Action:The state can not run. - %d" % virt[0].status())
                    
            elif status == GUEST_ACTION_SUSPEND:
                cmdname = ["Suspend Guest", "suspend guest"]
                if virt[0].is_suspendable() is True:
                    # -- Suspend
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_SUSPEND_GUEST),
                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_SUSPEND_GUEST
                else:
                    self.logger.error("Destroy Action:The state can not run. - %d" % virt[0].status())
                    
            elif status == GUEST_ACTION_RESUME:
                cmdname = ["Resume Guest", "resume guest"]
                if virt[0].is_resumable() is True:
                    # -- Resume
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_RESUME_GUEST),
                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_RESUME_GUEST
                else:
                    self.logger.error("Resume Action:The state can not run. - %d" % virt[0].status())

            elif status == GUEST_ACTION_REBOOT:
                cmdname = ["Reboot Guest", "reboot guest"]
                if virt[0].is_shutdownable() is True:
                    # -- Reboot
                    _cmd = dict2command(
                        "%s/%s" % (karesansui.config['application.bin.dir'],
                                   VIRT_COMMAND_REBOOT_GUEST),
                        {"name":domname})
                    
                    self.view.status = VIRT_COMMAND_REBOOT_GUEST
                else:
                    self.logger.error("Reboot Action:The state can not run. - %d" % virt[0].status())

            elif status == GUEST_ACTION_ENABLE_AUTOSTART:
                cmdname = ["Enable Autostart Guest", "enable autostart guest"]
                # -- Enable autostart guest
                _cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'],
                               VIRT_COMMAND_AUTOSTART_GUEST),
                    {"name":domname, "enable":None})
                    
                self.view.status = VIRT_COMMAND_AUTOSTART_GUEST

            elif status == GUEST_ACTION_DISABLE_AUTOSTART:
                cmdname = ["Disable Autostart Guest", "disable autostart guest"]
                # -- Disable autostart guest
                _cmd = dict2command(
                    "%s/%s" % (karesansui.config['application.bin.dir'],
                               VIRT_COMMAND_AUTOSTART_GUEST),
                    {"name":domname, "disable":None})
                    
                self.view.status = VIRT_COMMAND_AUTOSTART_GUEST

            else:
                self.logger.error("Action:Bad Request. - request status=%d" % status)
                return web.badrequest()

        finally:
            kvc.close()

        # Job Register
        _jobgroup = JobGroup(cmdname[0], karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('%s command' % cmdname[1], 0, _cmd))
        
        _machine2jobgroup = m2j_new(machine=model,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=self.me,
                                    modified_user=self.me,
                                    )
        
        # INSERT
        save_job_collaboration(self.orm,
                               self.pysilhouette.orm,
                               _machine2jobgroup,
                               _jobgroup,
                               )
        return web.accepted(url="/host/%d/guest/%d.part" % (host_id, guest_id))

urls = (
    '/host/(\d+)/guest/(\d+)/status/?(\.part|\.json)?$', GuestBy1Status,
    )
