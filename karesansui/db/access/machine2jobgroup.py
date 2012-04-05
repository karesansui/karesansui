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

from karesansui.lib.const import MACHINE_ATTRIBUTE
from karesansui.db.access import dbsave, dbupdate, dbdelete
from karesansui.db.model.machine2jobgroup import Machine2Jobgroup
from karesansui.db.access._2pysilhouette import jobgroup_findbyuniqkey

# -- all
def findbyall(session):
    return session.query(Machine2Jobgroup).all()

# -- one
def findby1(session, id):
    return session.query(
        Machine2Jobgroup).filter(
        Machine2Jobgroup.id == id).first()

# -- machine1
def findby1machine(session, machine_id):
    return session.query(
        Machine2Jobgroup).filter(
        Machine2Jobgroup.machine_id == machine_id).all()

# -- jobgroup1
def findby1jobgroup(session, jobgroup_id):
    return session.query(
        Machine2Jobgroup).filter(
        Machine2Jobgroup.jobgroup_id == jobgroup_id).all()

@dbdelete
def deleteby1machine(session, machine_id):
    return session.query(Machine2Jobgroup).filter(
        Machine2Jobgroup.machine_id == machine_id).delete()

@dbsave
def save(session, machine2jobgroup):
    session.save(machine2jobgroup)
    
@dbupdate
def update(session, machine2jobgroup):
    session.update(machine2jobgroup)
    
@dbdelete
def delete(session, machine2jobgroup):
    session.delete(machine2jobgroup)
    
# new instance
new = Machine2Jobgroup
