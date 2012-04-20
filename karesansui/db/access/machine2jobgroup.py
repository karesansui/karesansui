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
    session.add(machine2jobgroup)
    
@dbupdate
def update(session, machine2jobgroup):
    session.add(machine2jobgroup)
    
@dbdelete
def delete(session, machine2jobgroup):
    session.delete(machine2jobgroup)
    
# new instance
new = Machine2Jobgroup
