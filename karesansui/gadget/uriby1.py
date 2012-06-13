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
    comma_split, uniq_sort, is_param, json_dumps, uri_split, uri_join

from karesansui.lib.virt.virt import KaresansuiVirtConnectionURI

from karesansui.lib.merge import  MergeGuest, MergeHost

from karesansui.db.access.machine import \
     findbyhost1guestall, findbyhost1, \
     findbyguest1

from karesansui.db.access.machine import \
     findbyguest1, findby1name, logical_delete, \
     update as m_update, delete as m_delete

from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import save_job_collaboration

from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

class UriBy1(Rest):

    def _post(self, f):
        ret = Rest._post(self, f)
        if hasattr(self, "kvc") is True:
            self.kvc.close()
        return ret

    @auth
    def _GET(self, *param, **params):
        #import pdb; pdb.set_trace()

        host_id =  param[0]
        host_id = self.chk_hostby1(param)
        if host_id is None:
            return web.notfound()

        uri_id =  param[1]
        if uri_id is None:
            return web.notfound()

        model = findbyhost1(self.orm, host_id)

        if model.attribute == 2:
            info = {}
            segs = uri_split(model.hostname)
            uri = uri_join(segs, without_auth=True)
            creds = ''
            if segs["user"] is not None:
                creds += segs["user"]
                if segs["passwd"] is not None:
                    creds += ':' + segs["passwd"]

            # Output .part
            if self.is_mode_input() is not True:
                try:
                    self.kvc = KaresansuiVirtConnectionURI(uri,creds)
                    host = MergeHost(self.kvc, model)
                    for guest in host.guests:

                        _virt = self.kvc.search_kvg_guests(guest.info["model"].name)
                        if 0 < len(_virt):
                            #import pdb; pdb.set_trace()
                            info = _virt[0].get_info()
                            if info["uuid"] == uri_id:
                                __guest = MergeGuest(guest.info["model"], _virt[0])
                                autostart = _virt[0].autostart()
                                break

                    json_guest = __guest.get_json(self.me.languages)

                finally:
                    self.kvc.close()

                #import pdb; pdb.set_trace()
                # .json
                if self.__template__["media"] == 'json':
                    self.view.data = json_dumps(
                        {
                            "model": json_guest["model"],
                            "autostart": autostart,
                            "virt": json_guest["virt"],
                            "info": info,
                        }
                    )
                else:
                    self.view.model = __guest.info["model"]
                    self.view.autostart = autostart
                    self.view.virt = guest.info["virt"]
                    self.view.info = info


        return True

urls = (
    '/host/(\d+)/uri/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/?(\.html|\.part|\.json)?', UriBy1,
    )
