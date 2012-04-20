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
from web.utils import Storage

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.utils import is_param, json_dumps

from karesansui.lib.const import SERVICE_XML_FILE, \
     SERVICE_COMMAND_START, SERVICE_COMMAND_STOP, \
     SERVICE_COMMAND_RESTART, SERVICE_COMMAND_AUTOSTART

from karesansui.lib.service.config import ServiceConfigParam
from karesansui.lib.service.sysvinit_rh import SysVInit_RH

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

SERVICE_START = 0
SERVICE_STOP = 1
SERVICE_RESTART = 2
SERVICE_ENABLE = 3
SERVICE_DISABLE = 4

class HostBy1ServiceBy1Status(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id

        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()
        service = config.findby1service(param[1])
        if not service:
            self.logger.debug("Get service status failed. Service not found.")
            return web.notfound("Service not found")

        sysv = SysVInit_RH(service['system_name'], service['system_command'])
        status = {"status":sysv.status(),
                  "autostart":sysv.onboot(),
                  "readonly":service["system_readonly"],
                  }

        if self.__template__["media"] == 'json':
            self.view.status = json_dumps(status)
        else:
            self.view.status = status

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id

        host = findbyhost1(self.orm, host_id)

        name = param[1]
        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()
        service = config.findby1service(name)
        if not service:
            self.logger.debug("Set service status failed. Service not found.")
            return web.notfound("Service not found")

        if not is_param(self.input, 'status'):
            self.logger.error("Set service status failed. Missing request param.")
            return web.badrequest("Missing request param.")

        status = int(self.input.status)
        if status == SERVICE_START:
            service_job(self, host, name, "start")
        elif status == SERVICE_STOP:
            service_job(self, host, name, "stop")
        elif status == SERVICE_RESTART:
            service_job(self, host, name, "restart")
        elif status == SERVICE_ENABLE:
            service_job(self, host, name, "enable")
        elif status == SERVICE_DISABLE:
            service_job(self, host, name, "disable")
        else:
            self.logger.error("Set service status failed. Invalid request param.")
            return web.badrequest("Invalid request param")

        return web.accepted()

def service_job(obj, host, name, status):

    if status == 'start':
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], SERVICE_COMMAND_START),
            {"name" : name})
        cmdname = "Start Service"
    elif status == 'stop':
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], SERVICE_COMMAND_STOP),
            {"name" : name})
        cmdname = "Stop Service"
    elif status == 'restart':
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], SERVICE_COMMAND_RESTART),
            {"name" : name})
        cmdname = "Restart Service"
    elif status == 'enable':
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], SERVICE_COMMAND_AUTOSTART),
            {"name" : name, "enable": None})
        cmdname = "Enable Autostart Service"
    elif status == 'disable':
        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], SERVICE_COMMAND_AUTOSTART),
            {"name" : name, "disable": None})
        cmdname = "Disable Autostart Service"
    else:
        raise

    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _job = Job(cmdname, 0, _cmd)
    _jobgroup.jobs.append(_job)

    _machine2jobgroup = m2j_new(machine=host,
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

urls = (
    '/host/(\d+)/service/([a-zA-z\-]{4,32})/status/?(\.json)$', HostBy1ServiceBy1Status,
    )
