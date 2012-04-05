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
    session.save(snapshot)

@dbupdate
def update(session, snapshot):
    session.update(snapshot)
    
@dbdelete
def delete(session, snapshot):
    session.delete(snapshot)

# new instance
new = Snapshot
