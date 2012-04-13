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

from karesansui.db.model.option import Option
from karesansui.db.access import dbsave, dbupdate, dbdelete

# -- all
def findbyall(session):
    return session.query(Option).all()

def findby1(session, option_id):
    return session.query(Option).filter(Option.id == option_id).first()

def findby1key(session, key):
    return session.query(Option).filter(
        Option.key == key).first()

@dbdelete
def delete(session, mailtemplate):
    session.delete()

@dbsave
def save(session, option):
    session.save(option)

@dbupdate
def update(session, option):
    session.update(option)
    
# new instance
new = Option

def test(session):
    from karesansui.db.access.user import findby1 as user_findby1
    user = user_findby1(session, 1)
    import os
    option = Option(created_user=user,
                  modified_user=user,
                  key='key_%s' % str(os.getpid()),
                  value='hogehoge',
                  )
    import pdb; pdb.set_trace()
    
    save(session, option)
    session.commit()
    _all = findbyall(session)
    _findby1 = findby1(session, option.id)
    _findby1key = findby1key(session, option.key)
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    test()
