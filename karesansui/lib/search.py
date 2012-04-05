#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_ONLYSPACE
from karesansui.lib.const import SEARCH_MIN_LENGTH, SEARCH_MAX_LENGTH, \
    MACHINE_NAME_MIN_LENGTH, MACHINE_NAME_MAX_LENGTH, \
    USER_MIN_LENGTH, USER_MAX_LENGTH
from karesansui.db.model._2pysilhouette import JOBGROUP_STATUS
from karesansui.lib.utils import is_param

def validates_query(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'q'):
        check = checker.check_string(_('Search Query'),
                obj.input.q,
                CHECK_EMPTY | CHECK_LENGTH | CHECK_VALID,
                '[%_]',
                min = SEARCH_MIN_LENGTH,
                max = SEARCH_MAX_LENGTH,
                ) and check

    obj.view.alert = checker.errors
    return check

def validates_jobsearch(obj):
    checker = Checker()
    _ = obj._
    checker.errors = []
    
    check = True
    edit = False
    
    if is_param(obj.input, "name", True) is True:
        edit = True
        check = checker.check_string(
            _('Machine Name'),
            obj.input.name,
            CHECK_LENGTH | CHECK_ONLYSPACE | CHECK_VALID,
            '[%_]',
            min = MACHINE_NAME_MIN_LENGTH,
            max = MACHINE_NAME_MAX_LENGTH,
            ) and check

    if is_param(obj.input, "user", True) is True:
        edit = True
        check = checker.check_string(
            _('Create User'),
            obj.input.user,
            CHECK_LENGTH | CHECK_ONLYSPACE | CHECK_VALID,
            '[%_]',
            min = USER_MIN_LENGTH,
            max = USER_MAX_LENGTH,
            ) and check

    if is_param(obj.input, "status", True) is True:
        edit = True
        check = checker.check_status(
            _('Status'), 
            obj.input.status, 
            CHECK_VALID, 
            JOBGROUP_STATUS.values()
            ) and check

    if is_param(obj.input, "start", True) is True:
        edit = True
        check = checker.check_datetime_string(
            _('Created'),
            obj.input.start,
            CHECK_VALID,
            obj.me.languages
            ) and check
            
    if is_param(obj.input, "end", True) is True:
        edit = True
        check = checker.check_datetime_string(
            _('Created'),
            obj.input.end,
            CHECK_VALID,
            obj.me.languages
            ) and check

    obj.view.alert = checker.errors
    return check, edit

