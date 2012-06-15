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

import os
import web

import karesansui
from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import \
    comma_split, uniq_sort, is_param, json_dumps, \
    uri_split, uri_join

from karesansui.lib.virt.virt import KaresansuiVirtConnectionURI

from karesansui.lib.merge import  MergeGuest, MergeHost
from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

class UriGuestBy1(Rest):

    def _post(self, f):
        ret = Rest._post(self, f)
        if hasattr(self, "kvc") is True:
            self.kvc.close()
        return ret

    @auth
    def _GET(self, *param, **params):

        if self.input.has_key('job_id') is True:
            self.view.job_id = self.input.job_id
        else:
            self.view.job_id = None


        host_id =  param[0]
        host_id = self.chk_hostby1(param)
        if host_id is None:
            return web.notfound()

        uri_id =  param[1]
        if uri_id is None:
            return web.notfound()

        model = findbyhost1(self.orm, host_id)

        if self.is_mode_input() is False:
            if model.attribute == 2:
                info = {}
                segs = uri_split(model.hostname)
                uri = uri_join(segs, without_auth=True)
                creds = ''
                if segs["user"] is not None:
                    creds += segs["user"]
                    if segs["passwd"] is not None:
                        creds += ':' + segs["passwd"]
                self.kvc = KaresansuiVirtConnectionURI(uri,creds)

                try:
                    host = MergeHost(self.kvc, model)
                    for guest in host.guests:
                        _virt = self.kvc.search_kvg_guests(guest.info["model"].name)
                        if 0 < len(_virt):
                            for _v in _virt:
                                info = _v.get_info()
                                if info["uuid"] == uri_id:
                                    __guest = MergeGuest(guest.info["model"],_v)
                                    autostart       = _v.autostart()
                                    status          = _v.status()
                                    is_creatable    = _v.is_creatable()
                                    is_shutdownable = _v.is_shutdownable()
                                    is_suspendable  = _v.is_suspendable()
                                    is_resumable    = _v.is_resumable()
                                    is_destroyable  = _v.is_destroyable()
                                    is_active       = _v.is_active()
                                    break

                    if self.is_json() is True:
                        json_host  = host.get_json(self.me.languages)
                        json_guest = __guest.get_json(self.me.languages)
                        self.view.data = json_dumps(
                            {
                                "parent_model": json_host["model"],
                                "parent_virt": json_host["virt"],
                                "model": json_guest["model"],
                                "virt": json_guest["virt"],
                                "info": info,
                                "autostart": autostart,
                                "status": status,
                                "is_creatable": is_creatable,
                                "is_shutdownable": is_shutdownable,
                                "is_suspendable": is_suspendable,
                                "is_resumable": is_resumable,
                                "is_destroyable": is_destroyable,
                                "is_active": is_active,
                            }
                        )
                    else:
                        self.view.parent_model = host.info["model"]
                        self.view.parent_virt = host.info["virt"]
                        self.view.model = __guest.info["model"]
                        self.view.virt = __guest.info["virt"]
                        self.view.info = info
                        self.view.autostart = autostart
                        self.view.status = status
                        self.view.is_creatable = is_creatable
                        self.view.is_shutdownable = is_shutdownable
                        self.view.is_suspendable = is_suspendable
                        self.view.is_resumable = is_resumable
                        self.view.is_destroyable = is_destroyable
                        self.view.is_active = is_active
                finally:
                    self.kvc.close()

        return True




urls = (
    '/host/(\d+)/uriguest/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/?(\.html|\.part|\.json)?', UriGuestBy1,
    )
