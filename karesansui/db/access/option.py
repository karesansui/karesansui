#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
