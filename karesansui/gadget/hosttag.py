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
