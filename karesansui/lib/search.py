#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

