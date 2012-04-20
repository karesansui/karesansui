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

from karesansui.lib.rest import Rest, auth
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_CHAR
from karesansui.lib.utils import is_param, json_dumps
from karesansui.db.access.tag import findbyhostall, findbyhostall

class HostTag(Rest):
    @auth
    def _GET(self, *param, **params):
        tags = findbyhostall(self.orm)
        if not tags:
            return web.notfound(self._("No tag"))

        if self.is_part() is True:
            self.view.tags = tags
            machine_ids = {} 
            for tag in tags:
                tag_id = str(tag.id)

                machine_ids[tag_id] = []
                for machine in tag.machine:
                    machine_ids[tag_id].append("tag_machine%s"%  machine.id)

                machine_ids[tag_id]  = " ".join(machine_ids[tag_id])

            self.view.machine_ids = machine_ids

            return True

        elif self.is_json() is True:
            tags_json = []
            for tag in tags:
                tags_json.append(tag.get_json(self.me.languages))

            self.view.tags = json_dumps(tags_json)

            return True
        
        else:
            return web.nomethod()

urls = (
    '/host/tag/?(\.part|\.json)$', HostTag,
    )
