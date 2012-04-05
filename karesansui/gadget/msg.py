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

from karesansui import sheconf
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import MSG_LIMIT, DEFAULT_LANGS
from karesansui.lib.template import total_progress
from karesansui.db.model._2pysilhouette import JOBGROUP_STATUS
from karesansui.db.access._2pysilhouette import jg_findbyserial_limit
from karesansui.db.access.machine2jobgroup import findby1jobgroup as m2j_find

class Msg(Rest):

    @auth
    def _GET(self, *param, **params):
        uniq_key = sheconf['env.uniqkey']
        jgs = jg_findbyserial_limit(self.pysilhouette.orm,
                            MSG_LIMIT,
                            True)
        msgs = []
        for jg in jgs:
            msg = {}
            m2j = m2j_find(self.orm, jg.id)
            msg['id'] = jg.id
            msg['name'] = jg.name
            if m2j == []:
                msg['machine_name'] = None
                msg['user_name'] = None
            else:
                try:
                    msg['machine_id'] = m2j[0].machine.id
                except:
                    msg['machine_id'] = "Unknown"

                try:
                    msg['machine_parent_id'] = m2j[0].machine.parent_id
                except:
                    msg['machine_parent_id'] = "Unknown"

                try:
                    msg['machine_name'] = m2j[0].machine.name
                except:
                    msg['machine_name'] = "Unknown"

                try:
                    msg['machine_attr'] = m2j[0].machine.attribute
                except:
                    msg['machine_attr'] = "Unknown"

                try:
                    msg['user_name'] = m2j[0].machine.created_user.nickname
                except:
                    msg['user_name'] = "Unknown"

            msg['status'] = jg.status
            msg['progress'] = total_progress(jg.jobs)
            msg['created'] = jg.created
            msg['modified'] = jg.modified
            msgs.append(msg)

        self.view.msgs = msgs
        self.view.JOBGROUP_STATUS = JOBGROUP_STATUS
        self.view.date_format = DEFAULT_LANGS[self.me.languages]['DATE_FORMAT'][1]
        return True

urls = (
    '/msg/?(\.part)$', Msg
    )
