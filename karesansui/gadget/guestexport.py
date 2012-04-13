# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
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

import os
import re
import glob
import time

import web
import simplejson as json

import karesansui
from karesansui.gadget.guest import regist_guest
from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import chk_create_disk, json_dumps, is_param, base64_encode, get_partition_info
from karesansui.lib.const import \
    VIRT_COMMAND_EXPORT_GUEST, \
    ID_MIN_LENGTH, ID_MAX_LENGTH, \
    NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH

from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.virt.config_export import ExportConfigParam

from karesansui.db.access.machine import findbyguest1
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration

from pysilhouette.command import dict2command
from karesansui.db.model._2pysilhouette import Job, JobGroup

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_ONLYSPACE, \
    CHECK_MIN, CHECK_MAX

def validates_guest_export(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'export_title'):
        check = False
        checker.add_error(_('Parameter export_title does not exist.'))
    else:
        check = checker.check_string(
                    _('Title'),
                    obj.input.export_title,
                    CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = NOTE_TITLE_MIN_LENGTH,
                    max = NOTE_TITLE_MAX_LENGTH,
                ) and check

    obj.view.alert = checker.errors
    return check

def validates_sid(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'sid'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Copy Source'))
    else:
        check = checker.check_number(_('Copy Source'),
                                     obj.input.sid,
                                     CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     ID_MIN_LENGTH,
                                     ID_MAX_LENGTH
                                     ) and check

        obj.view.alert = checker.errors
    return check


class GuestExport(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        kvc = KaresansuiVirtConnection()
        try:
            # Storage Pool
            #inactive_pool = kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            if self.is_mode_input() is True: # (*.input)
                if not validates_sid(self):
                    return web.badrequest(self.view.alert)

                sid = self.input.sid
                model = findbyguest1(self.orm, sid)
                if not model:
                    return web.badrequest()

                domname = kvc.uuid_to_domname(model.uniq_key)

                src_pools = kvc.get_storage_pool_name_bydomain(domname)
                if not src_pools:
                    return web.badrequest(_("Source storage pool is not found."))

                for src_pool in  src_pools :
                    src_pool_type = kvc.get_storage_pool_type(src_pool)
                    if src_pool_type != 'dir':
                        return web.badrequest(_("'%s' disk contains the image.") % src_pool_type)

                virt = kvc.search_kvg_guests(domname)[0]

                if virt.is_active() is True:
                    return web.badrequest(_("Guest is running. Please stop and try again. name=%s" % domname))

                self.view.domname = virt.get_domain_name()

                non_iscsi_pool = []
                for pool in pools:
                    if kvc.get_storage_pool_type(pool) != 'iscsi':
                        non_iscsi_pool.append(pool)
                self.view.pools = non_iscsi_pool
                self.view.sid = sid
                return True

            # Exported Guest Info (*.json)
            exports = {}
            for pool_name in pools:
                files = []
                pool = kvc.search_kvn_storage_pools(pool_name)
                path = pool[0].get_info()["target"]["path"]

                if os.path.exists(path):
                    for _afile in glob.glob("%s/*/info.dat" % (path,)):
                        param = ExportConfigParam()
                        param.load_xml_config(_afile)

                        _dir = os.path.dirname(_afile)

                        uuid = param.get_uuid()
                        name = param.get_domain()
                        created = param.get_created()
                        title = param.get_title()
                        if title != "":
                            title = re.sub("[\r\n]","",title)
                        if title == "":
                            title = _('untitled')

                        if created != "":
                            created_str = time.strftime("%Y/%m/%d %H:%M:%S", \
                                                        time.localtime(float(created)))
                        else:
                            created_str = _("N/A")

                        files.append({"dir": _dir,
                                      "pool" : pool_name,
                                      #"b64dir" : base64_encode(_dir),
                                      "uuid" : uuid,
                                      "name" : name,
                                      "created" : int(created),
                                      "created_str" : created_str,
                                      "title" : title,
                                      })

                exports[pool_name] = files

                # .json
                if self.is_json() is True:
                    self.view.exports = json_dumps(exports)
                else:
                    self.view.exports = exports

            return True

        finally:
            kvc.close()

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_guest_export(self):
            return web.badrequest(self.view.alert)

        if not validates_sid(self):
            return web.badrequest(self.view.alert)

        model = findbyguest1(self.orm, self.input.sid)
        if not model:
            return web.badrequest()

        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(model.uniq_key)
            if not domname: return web.conflict(web.ctx.path)

            src_pools = kvc.get_storage_pool_name_bydomain(domname)
            if not src_pools:
                return web.badrequest(_("Source storage pool is not found."))

            for src_pool in  src_pools :
                src_pool_type = kvc.get_storage_pool_type(src_pool)
                if src_pool_type != 'dir':
                    return web.badrequest(_("'%s' disk contains the image.") % src_pool_type)

            virt = kvc.search_kvg_guests(domname)[0]
            options = {}
            options["name"] = virt.get_domain_name()
            if is_param(self.input, "pool"):
                # disk check
                src_pool = kvc.get_storage_pool_name_bydomain(domname, 'os')[0]
                src_path = kvc.get_storage_pool_targetpath(src_pool)
                src_disk = "%s/%s/images/%s.img" \
                           % (src_path, options["name"], options["name"])

                dest_path = kvc.get_storage_pool_targetpath(self.input.pool)
                s_size = os.path.getsize(src_disk) / (1024 * 1024) # a unit 'MB'

                if os.access(dest_path, os.F_OK):
                    if chk_create_disk(dest_path, s_size) is False:
                        partition = get_partition_info(dest_path, header=False)
                        return web.badrequest(
                            _("No space available to create disk image in '%s' partition.") \
                                % partition[5][0])

                #else: # Permission denied
                    #TODO:check disk space for root

                options["pool"] = self.input.pool

            if is_param(self.input, "export_title"):
                #options["title"] = self.input.export_title
                options["title"] = "b64:" + base64_encode(self.input.export_title)
            options["quiet"] = None

        finally:
            kvc.close()

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_EXPORT_GUEST), options)

        # Job Register
        cmdname = ["Export Guest", "export guest"]
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

        self.logger.debug("(%s) Job group id==%s" % (cmdname[0],_jobgroup.id))
        url = '%s/job/%s.part' % (web.ctx.home, _jobgroup.id)
        self.logger.debug('Returning Location: %s' % url)

        return web.accepted()

urls = (
    '/host/(\d+)/guestexport/?(\.part|\.json)$', GuestExport,
    )
