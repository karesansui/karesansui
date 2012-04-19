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

from karesansui.db.model.snapshot import Snapshot
from karesansui.db.access import dbsave, dbupdate, dbdelete

# -- all
def findbyall(session, is_deleted=False):
    return session.query(Snapshot).filter(
        Snapshot.is_deleted == is_deleted).all()

def findby1(session, snapshot_id, is_deleted=False):
    return session.query(Snapshot).filter(
        Snapshot.id == snapshot_id).filter(
        Snapshot.is_deleted == is_deleted).first()


def is_findby1_guestby1(session, snapshot_id, guest_id, is_deleted=False):
    return session.query(Snapshot).filter(
        Snapshot.id == snapshot_id).filter(
        Snapshot.machine_id == guest_id).filter(
        Snapshot.is_deleted == is_deleted).count()

def findbyname(session, name, is_deleted=False):
    return session.query(Snapshot).filter(
        Snapshot.name == name).filter(
        Snapshot.is_deleted == is_deleted).first()

def findbyname_guestby1(session, name, guest_id, is_deleted=False):
    return session.query(Snapshot).filter(
        Snapshot.name == name).filter(
        Snapshot.machine_id == guest_id).filter(
        Snapshot.is_deleted == is_deleted).first()

def logical_delete(session, snapshot):
    snapshot.is_deleted = True
    return update(session, snapshot)

@dbsave
def save(session, snapshot):
    session.add(snapshot)

@dbupdate
def update(session, snapshot):
    session.add(snapshot)
    
@dbdelete
def delete(session, snapshot):
    session.delete(snapshot)

# new instance
new = Snapshot
