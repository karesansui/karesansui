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

import os.path
import re
import glob
import time

import web
import simplejson as json

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.virt.config import ConfigParam
from karesansui.lib.virt.config_export import ExportConfigParam

from karesansui.lib.const import VIRT_COMMAND_DELETE_EXPORT_DATA

from karesansui.lib.utils import json_dumps

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access.notebook import findby1 as n_findby1
from karesansui.db.access.machine  import findbyhost1

from pysilhouette.command import dict2command
from karesansui.db.model._2pysilhouette import Job, JobGroup

class GuestExportBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        # valid
        self.view.uuid = param[1]

        kvc = KaresansuiVirtConnection()
        try: # libvirt connection scope -->
            # Storage Pool
            #inactive_pool = kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            export = []
            for pool_name in pools:
                pool = kvc.search_kvn_storage_pools(pool_name)
                path = pool[0].get_info()["target"]["path"]
                if os.path.exists(path):
                    for _afile in glob.glob("%s/*/info.dat" % (path,)):
                        e_param = ExportConfigParam()
                        e_param.load_xml_config(_afile)

                        if e_param.get_uuid() != self.view.uuid:
                            continue

                        e_name = e_param.get_domain()
                        _dir = os.path.dirname(_afile)

                        param = ConfigParam(e_name)

                        path = "%s/%s.xml" % (_dir, e_name)
                        if os.path.isfile(path) is False:
                            self.logger.error('Export corrupt data.(file not found) - path=%s' % path)
                            return web.internalerror()

                        param.load_xml_config(path)

                        if e_name != param.get_domain_name():
                            self.logger.error('Export corrupt data.(The name does not match) - info=%s, xml=%s' \
                                              % (e_name, param.get_name()))
                            return web.internalerror()

                        _dir = os.path.dirname(_afile)

                        title = e_param.get_title()
                        if title != "":
                            title = re.sub("[\r\n]","",title)
                        if title == "":
                            title = _('untitled')

                        created = e_param.get_created()
                        if created != "":
                            created_str = time.strftime("%Y/%m/%d %H:%M:%S", \
                                                        time.localtime(float(created)))
                        else:
                            created_str = _("N/A")

                        export.append({"info" : {"dir" : _dir,
                                                 "pool" : pool_name,
                                                 "uuid" : e_param.get_uuid(),
                                                 "name" : e_name,
                                                 "created" : int(created),
                                                 "created_str" : created_str,
                                                 "title" : title,
                                                  },
                                       "xml" : {"on_reboot" : param.get_behavior('on_reboot'),
                                                "on_poweroff" : param.get_behavior('on_poweroff'),
                                                "on_crash" : param.get_behavior('on_crash'),
                                                "boot_dev" : param.get_boot_dev(),
                                                #"bootloader" : param.get_bootloader(),
                                                #"commandline" : param.get_commandline(),
                                                #"current_snapshot" : param.get_current_snapshot(),
                                                'disk' : param.get_disk(),
                                                "domain_name" : param.get_domain_name(),
                                                "domain_type" : param.get_domain_type(),
                                                "features_acpi" : param.get_features_acpi(),
                                                "features_apic" : param.get_features_apic(),
                                                "features_pae" : param.get_features_pae(),
                                                #"initrd" : param.get_initrd(),
                                                "interface" : param.get_interface(),
                                                #"kernel" : param.get_kernel(),
                                                "max_memory" : param.get_max_memory(),
                                                'max_vcpus' : param.get_max_vcpus(),
                                                "max_vcpus_limit" : param.get_max_vcpus_limit(),
                                                "memory" : param.get_memory(),
                                                "uuid" : param.get_uuid(),
                                                "vcpus" : param.get_vcpus(),
                                                "vcpus_limit" : param.get_vcpus_limit(),
                                                "graphics_autoport" : param.get_graphics_autoport(),
                                                "keymap" : param.get_graphics_keymap(),
                                                "graphics_listen" : param.get_graphics_listen(),
                                                "graphics_passwd" : param.get_graphics_passwd(),
                                                "graphics_port" : param.get_graphics_port(),
                                                },
                                       "pool" : pool[0].get_info(),
                                       })

            if len(export) != 1:
                self.logger.info("Export does not exist. - uuid=%s" % self.view.uuid)
                return web.badrequest()

            # .json
            if self.is_json() is True:
                self.view.export = json_dumps(export[0])
            else:
                self.view.export = export

            return True
        finally:
            kvc.close() 

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        # valid
        self.view.uuid = param[1]

        kvc = KaresansuiVirtConnection()
        try:
            # Storage Pool
            #inactive_pool = kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            export = []
            for pool_name in pools:
                pool = kvc.search_kvn_storage_pools(pool_name)
                path = pool[0].get_info()["target"]["path"]
                if os.path.exists(path):
                    for _afile in glob.glob("%s/*/info.dat" % (path,)):
                        e_param = ExportConfigParam()
                        e_param.load_xml_config(_afile)

                        if e_param.get_uuid() != self.view.uuid:
                            continue

                        e_name = e_param.get_domain()
                        _dir = os.path.dirname(_afile)

                        param = ConfigParam(e_name)

                        path = "%s/%s.xml" % (_dir, e_name)
                        if os.path.isfile(path) is False:
                            self.logger.error('Export corrupt data.(file not found) - path=%s' % path)
                            return web.internalerror()

                        param.load_xml_config(path)

                        if e_name != param.get_domain_name():
                            self.logger.error('Export corrupt data.(The name does not match) - info=%s, xml=%s' \
                                              % (e_name, param.get_name()))
                            return web.internalerror()

                        _dir = os.path.dirname(_afile)

                        export.append({"dir" : _dir,
                                       "pool" : pool_name,
                                       "uuid" : e_param.get_uuid(),
                                       "name" : e_name,
                                       })

            if len(export) != 1:
                self.logger.info("Export does not exist. - uuid=%s" % self.view.uuid)
                return web.badrequest()
        finally:
            kvc.close()

        export = export[0]
        if os.path.exists(export['dir']) is False or os.path.isdir(export['dir']) is False:
            self.logger.error('Export data is not valid. [%s]' % export_dir)
            return web.badrequest('Export data is not valid.')

        host = findbyhost1(self.orm, host_id)

        options = {}
        options['uuid'] = export["uuid"]

        _cmd = dict2command("%s/%s" % (karesansui.config['application.bin.dir'], \
                                       VIRT_COMMAND_DELETE_EXPORT_DATA), options)

        # Job Registration
        _jobgroup = JobGroup('Delete Export Data', karesansui.sheconf['env.uniqkey'])

        _jobgroup.jobs.append(Job('Delete Export Data', 0, _cmd))

        _machine2jobgroup = m2j_new(machine=host,
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

        self.logger.debug('(Delete export data) Job group id==%s', _jobgroup.id)
        url = '%s/job/%s.part' % (web.ctx.home, _jobgroup.id)
        self.logger.debug('Returning Location: %s' % url)

        return web.accepted()

urls = (
    '/host/(\d+)/guestexport/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})/?(\.json)$', GuestExportBy1,
    )
