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

from karesansui.db.model.notebook import Notebook
from karesansui.db.access import dbsave, dbupdate, dbdelete

# -- all
def findbyall(session):
    return session.query(Notebook).all()

def findby1(session, notebook_id):
    if notebook_id:
        return session.query(Notebook).filter(Notebook.id == notebook_id).first()
    else:
        return None

@dbsave
def save(session, notebook):
    session.save(notebook)

@dbupdate
def update(session, notebook):
    session.update(notebook)
    
@dbdelete
def delete(session, notebook):
    session.delete(notebook)

# new instance
new = Notebook
