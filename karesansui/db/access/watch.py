#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

from sqlalchemy import and_, or_

from karesansui.db.model.watch import Watch
from karesansui.db.model.machine import Machine
from karesansui.db.access import dbsave, dbupdate, dbdelete
from karesansui.db.access.search import findbyand as _findbyand, \
     findbyor as _findbyor

# -- all
def findbyall(session, is_deleted=False):
    return session.query(Watch).filter(
        Watch.is_deleted == is_deleted).all()

def findby1(session, watch_id, is_deleted=False):
    return session.query(Watch).filter(
        Watch.id == watch_id).filter(
        Watch.is_deleted == is_deleted).first()

def findbyallmachine(session, machine, is_deleted=False):
    return session.query(Watch).filter(
        Watch.machine_id == machine.id).filter(
        Watch.is_deleted == is_deleted).all()

def findbyallplugin(session, plugin, is_deleted=False):
    return session.query(Watch).filter(
        Watch.plugin == plugin).filter(
        Watch.is_deleted == is_deleted).all()

def findby1name(session, name, is_deleted=False):
    return session.query(Watch).filter(
        Watch.name == name).filter(
        Watch.is_deleted == is_deleted).first()

def findbyand(session, query):
    return _findbyand(session, query, Watch, [Watch.name])

def findbyname_or_plugin(session, query):
    ret = _findbyor(session, query, Watch, [Watch.name, Watch.plugin])
    return ret 

def is_uniq_duplication(session, machine, plugin, plugin_selector, is_deleted=False):
    and_clause = and_()
    and_clause.append(Watch.machine_id == machine.id)
    and_clause.append(Watch.plugin == plugin)
    and_clause.append(Watch.plugin_selector == plugin_selector)
    and_clause.append(Watch.is_deleted == is_deleted)

    ret = session.query(Watch).filter(and_clause).all()

    if 1 <= len(ret):
        return True
    else:
        return False


@dbupdate
def logical_delete(session, watch):
    watch.is_deleted = True
    return session.add(watch)

@dbsave
def save(session, watch):
    session.add(watch)

@dbupdate
def update(session, watch):
    session.add(watch)
    
# new instance
new = Watch

def test(session):
    from karesansui.db.access.user import findby1 as user_findby1
    user = user_findby1(session, 1)
    from karesansui.db.access.machine import findby1 as machine_findby1
    machine = machine_findby1(session, 1)

    plugin_selector = """<Match>
plugin hoge
</Match>"""

    warning_mail_body = """To: to@example.com
From: spam <from@example.com>
Subject: warning mail!!
Mime-Version: 1.0
Content-Type: text/plain; charset=ISO-2022-JP
Content-Transfer-Encoding: 7bit

warning
"""
    failure_mail_body = """To: to@example.com
From: spam <from@example.com>
Subject: warning mail!!
Mime-Version: 1.0
Content-Type: text/plain; charset=ISO-2022-JP
Content-Transfer-Encoding: 7bit

warning
"""
    okay_mail_body = """To: to@example.com
From: spam <from@example.com>
Subject: warning mail!!
Mime-Version: 1.0
Content-Type: text/plain; charset=ISO-2022-JP
Content-Transfer-Encoding: 7bit

warning
"""
    import os
    watch = Watch(created_user=user,
                  modified_user=user,
                  machine=machine,
                  name='dummy_watch_%s' % str(os.getpid()),
                  plugin='cpu',
                  plugin_selector=plugin_selector,
                  karesansui_version='1.2.0',
                  collectd_version='4.9.1',
                  continuation_count=1,
                  prohibition_period=1,
                  warning_value="warning_value",
                  is_warning_percentage=True,
                  is_warning_script=False,
                  warning_script="warning_script",
                  is_warning_mail=True,
                  warning_mail_body=warning_mail_body,
                  failure_value="failure_value",
                  is_failure_percentage=True,
                  is_failure_script=True,
                  failure_script="failure_script",
                  is_failure_mail=True,
                  failure_mail_body=failure_mail_body,
                  is_okay_script=True,
                  okay_script="okay_script",
                  is_okay_mail=True,
                  okay_mail_body=okay_mail_body,
                  notify_mail_to='to@example.com',
                  notify_mail_from='from@example.com',
                  is_deleted=False,
                  )

    save(session, watch)
    session.commit()
    _all = findbyall(session)
    _findby1 = findby1(session, watch.id)
    _findbyallmachine = findbyallmachine(session, watch.machine)
    _findbyallplugin = findbyallplugin(session, watch.plugin)
    _findby1name = findby1name(session, watch.name)
    _findbyname_or_plugin = findbyname_or_plugin(session, 'mmy')
    _is_uniq_duplication = is_uniq_duplication(session, 'dummy_watch_13161', 'cpu', machine)
    import pdb; pdb.set_trace()
    print ''

if __name__ == '__main__':
    test()
