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
from karesansui.gadget.guest import regist_guest
from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import chk_create_disk, json_dumps, is_param, \
  base64_encode, base64_decode, get_dom_list, get_dom_type, \
  string_from_uuid, generate_uuid, comma_split, uniq_sort, get_partition_info

from karesansui.lib.const import \
    VIRT_COMMAND_IMPORT_GUEST

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.virt.config import ConfigParam
from karesansui.lib.virt.config_export import ExportConfigParam

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration

from pysilhouette.command import dict2command
from karesansui.db.model._2pysilhouette import Job, JobGroup

from karesansui.db.access.machine  import new as m_new, findby1uniquekey as m_findby1uniquekey
from karesansui.db.access.notebook import new as n_new
from karesansui.db.access.tag      import new as t_new
from karesansui.db.access.machine  import findby1 as m_findby1
from karesansui.db.access.notebook import findby1 as n_findby1
from karesansui.db.access.tag      import findby1 as t_findby1
from karesansui.db.access.tag      import samecount   as t_count
from karesansui.db.access.tag      import findby1name as t_name

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_ISDIR, CHECK_STARTROOT, CHECK_EXIST

from karesansui.lib.utils import get_xml_parse        as XMLParse
from karesansui.lib.utils import get_xml_xpath        as XMLXpath
from karesansui.lib.utils import get_nums_xml_xpath   as XMLXpathNum
from karesansui.lib.file.configfile import ConfigFile

def validates_guest_import(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []
    # TODO UUID check

    obj.view.alert = checker.errors
    return check


class GuestImport(Rest):

    #@auth
    #def _GET(self, *param, **params):
    #    return web.seeother()

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        model = findbyhost1(self.orm, host_id)

        if not validates_guest_import(self):
            return web.badrequest(self.view.alert)

        uuid = self.input.uuid
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

                        if e_param.get_uuid() != uuid:
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
                                                 "name" : e_param.get_domain(),
                                                 "created" : int(created),
                                                 "created_str" : created_str,
                                                 "title" : title,
                                                 "database" : {"name" : e_param.database["name"],
                                                               "tags" : e_param.database["tags"],
                                                               "attribute" : e_param.database["attribute"],
                                                               "notebook" : {"title" : e_param.database["notebook"]["title"],
                                                                             "value" : e_param.database["notebook"]["value"],
                                                                             },
                                                               "uniq_key" : e_param.database["uniq_key"],
                                                               "hypervisor" : e_param.database["hypervisor"],
                                                               "icon" : e_param.database["icon"],
                                                               },
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
            else:
                export = export[0]
        finally:
            kvc.close()

        # Pool running?
        if export['pool']['is_active'] is False:
            return web.badrequest("The destination, the storage pool is not running.")

        dest_domname = export['xml']['domain_name']
        dest_uniqkey = export['info']['database']['uniq_key']
        # Same guest OS is already running.
        if m_findby1uniquekey(self.orm, dest_uniqkey) is not None:
            self.logger.info(_("guest '%s' already exists. (DB) - %s") % (dest_domname, dest_uniqkey))
            return web.badrequest(_("guest '%s' already exists.") % dest_domname)

        dest_dir = "%s/%s" % (export['pool']['target']['path'], export['xml']['domain_name'])
        if os.path.exists(dest_dir) is True:
            self.logger.info(_("guest '%s' already exists. (FS) - %s") % (dest_domname, dest_dir))
            return  web.badrequest(_("guest '%s' already exists.") % dest_domname)

        # disk check
        try:
            src_disk = "%s/%s/images/%s.img" \
                       % (export["info"]["dir"], export["info"]["name"], export["info"]["name"])

            if os.path.exists(src_disk):
                s_size = os.path.getsize(src_disk) / (1024 * 1024) # a unit 'MB'
                if chk_create_disk(export["info"]["dir"], s_size) is False:
                    partition = get_partition_info(export["info"]["dir"], header=False)
                    return web.badrequest(
                        _("No space available to create disk image in '%s' partition.") \
                        % partition[5][0])
        except:
            pass

        extra_uniq_key = string_from_uuid(generate_uuid())
        options = {}
        options["exportuuid"] = export["info"]["uuid"]
        options["destuuid"] = extra_uniq_key
        options["quiet"] = None

        # Database Notebook
        try:
            _notebook = n_new(
                export["info"]["database"]["notebook"]["title"],
                export["info"]["database"]["notebook"]["value"],
                )
        except:
            _notebook = None

        # Database Tag
        _tags = []
        try:
            tag_array = comma_split(export["info"]["database"]["tags"])
            tag_array = uniq_sort(tag_array)
            for x in tag_array:
                if t_count(self.orm, x) == 0:
                    _tags.append(t_new(x))
                else:
                    _tags.append(t_name(self.orm, x))
        except:
            _tags.append(t_new(""))

        parent = m_findby1(self.orm, host_id)
        dest_guest = m_new(created_user=self.me,
                           modified_user=self.me,
                           uniq_key=extra_uniq_key,
                           name=export["info"]["database"]["name"],
                           attribute=int(export["info"]["database"]["attribute"]),
                           hypervisor=int(export["info"]["database"]["hypervisor"]),
                           notebook=_notebook,
                           tags=_tags,
                           icon=export["info"]["database"]["icon"],
                           is_deleted=False,
                           parent=parent,
                           )

        ret = regist_guest(self,
                           _guest=dest_guest,
                           icon_filename=export["info"]["database"]["icon"],
                           cmd=VIRT_COMMAND_IMPORT_GUEST,
                           options=options,
                           cmdname=['Import Guest', 'Import Guest'],
                           rollback_options={"name" : export["xml"]["domain_name"]},
                           is_create=False
                           )

        if ret is True:
            return web.accepted()
        else:
            return False

urls = (
    '/host/(\d+)/guestimport/?(\.part)$', GuestImport,
    )
