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
from karesansui import config

from karesansui.lib.rest import Rest, auth

from karesansui.lib.utils import generate_uuid, string_from_uuid, \
     uni_force, is_param, comma_split, uniq_sort

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_LENGTH, CHECK_ONLYSPACE, CHECK_VALID, \
    CHECK_MIN, CHECK_MAX

from karesansui.lib.const import \
    NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH, \
    MACHINE_NAME_MIN_LENGTH, MACHINE_NAME_MAX_LENGTH, \
    TAG_MIN_LENGTH, TAG_MAX_LENGTH, \
    FQDN_MIN_LENGTH, FQDN_MAX_LENGTH, \
    PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    MACHINE_ATTRIBUTE, MACHINE_HYPERVISOR

from karesansui.db.access.machine import \
     findbyhostall, findby1uniquekey, findby1hostname, \
     new as m_new, save as m_save, update as m_update
from karesansui.db.access.tag import new as t_new, \
     samecount as t_count, findby1name as t_name
from karesansui.db.access.notebook import new as n_new

def validates_host_add(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'm_name'):
        check = False
        checker.add_error(_('Parameter m_name does not exist.'))
    else:
        check = checker.check_string(
                    _('Machine Name'),
                    obj.input.m_name,
                    CHECK_EMPTY | CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = MACHINE_NAME_MIN_LENGTH,
                    max = MACHINE_NAME_MAX_LENGTH,
            ) and check

    if not is_param(obj.input, 'm_hostname'):
        check = False
        checker.add_error(_('"%s" is required.') % _('FQDN'))
    else:
        m_hostname_parts = obj.input.m_hostname.split(":")
        if len(m_hostname_parts) > 2:
            check = False
            checker.add_error(_('%s contains too many colon(:)s.') % _('FQDN'))
        else:
            check = checker.check_domainname(
                        _('FQDN'),
                        m_hostname_parts[0],
                        CHECK_EMPTY | CHECK_LENGTH | CHECK_VALID,
                        min = FQDN_MIN_LENGTH,
                        max = FQDN_MAX_LENGTH,
                        ) and check
            try:
                check = checker.check_number(
                            _('Port Number'),
                            m_hostname_parts[1],
                            CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                            PORT_MIN_NUMBER,
                            PORT_MAX_NUMBER,
                            ) and check
            except IndexError:
                # when reach here, 'm_hostname' has only host name
                pass

    if not is_param(obj.input, 'm_uuid'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Unique Key'))
    else:
        check = checker.check_unique_key(
                    _('Unique Key'),
                    obj.input.m_uuid,
                    CHECK_EMPTY | CHECK_VALID
                    ) and check

    if is_param(obj.input, 'note_title'):
        check = checker.check_string(
                    _('Title'),
                    obj.input.note_title,
                    CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = NOTE_TITLE_MIN_LENGTH,
                    max = NOTE_TITLE_MAX_LENGTH,
                ) and check

    if is_param(obj.input, 'note_value'):
        check = checker.check_string(
                    _('Note'),
                    obj.input.note_value,
                    CHECK_ONLYSPACE,
                    None,
                    None,
                    None,
                ) and check

    if is_param(obj.input, 'tags'):
        for tag in comma_split(obj.input.tags):
            check = checker.check_string(
                        _('Tag'),
                        tag,
                        CHECK_LENGTH | CHECK_ONLYSPACE,
                        None,
                        min = TAG_MIN_LENGTH,
                        max = TAG_MAX_LENGTH,
                    ) and check

    obj.view.alert = checker.errors
    return check

class Host(Rest):

    @auth
    def _GET(self, *param, **params):

        if self.is_mode_input():
            return True
        else:
            self.view.hosts = findbyhostall(self.orm)
            self.view.application_uniqkey = karesansui.config['application.uniqkey']
            if self.input.has_key('job_id') is True:
                self.view.job_id = self.input.job_id
            else:
                self.view.job_id = None
            
            return True

    @auth
    def _POST(self, *param, **params):
        if not validates_host_add(self):
            return web.badrequest(self.view.alert)

        uniq_key_check = findby1uniquekey(self.orm, self.input.m_uuid)
        if uniq_key_check is not None and config['application.uniqkey'] != self.input.m_uuid:
            return web.conflict(web.ctx.path)

        hostname_check = findby1hostname(self.orm, self.input.m_hostname)
        if hostname_check is not None:
            return web.conflict(web.ctx.path)

        # notebook
        note_title = None
        if is_param(self.input, "note_title"):
            note_title = self.input.note_title

        note_value = None
        if is_param(self.input, "note_value"):
            note_value = self.input.note_value
            
        _notebook = n_new(note_title, note_value)

        # tags
        _tags = None
        if is_param(self.input, "tags"):
            _tags = []
            tag_array = comma_split(self.input.tags)
            tag_array = uniq_sort(tag_array)
            for x in tag_array:
                if t_count(self.orm, x) == 0:
                    _tags.append(t_new(x))
                else:
                    _tags.append(t_name(self.orm, x))

        uniq_key = self.input.m_uuid
        name = self.input.m_name
        hostname = self.input.m_hostname

        model = findby1uniquekey(self.orm, uniq_key, is_deleted = True)
        if model is None:
            host = m_new(created_user=self.me,
                         modified_user=self.me,
                         uniq_key=uni_force(uniq_key),
                         name=name,
                         hostname=hostname,
                         attribute=MACHINE_ATTRIBUTE['HOST'],
                         hypervisor=MACHINE_HYPERVISOR['REAL'],
                         notebook=_notebook,
                         tags=_tags,
                         icon=None,
                         is_deleted=False)

            m_save(self.orm, host)
            return web.created(None)
        else:
            model.name = name
            model.hostname = hostname
            model.uniq_key = uniq_key
            model.notebook.title = note_title
            model.notebook.value = note_value
            model.tags = _tags
            model.is_deleted = False
            m_update(self.orm, model)
            return web.created(None)

urls = ('/host/?(\.html|\.part)$', Host)
