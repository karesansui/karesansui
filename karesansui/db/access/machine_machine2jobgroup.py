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
from karesansui.db.model.machine import Machine
from karesansui.db.model.machine2jobgroup import Machine2Jobgroup
from sqlalchemy import or_, and_

def findbyall(session, machine_name=None, created_start=None,
              created_end=None, created_user_id=None, desc=False):

    query = session.query(Machine).add_entity(Machine2Jobgroup).join(Machine2Jobgroup)

    if machine_name:
        query = query.filter(Machine.name.like(u"%%%s%%" % machine_name))

    if not created_user_id is None:
        query = query.filter(Machine2Jobgroup.created_user_id.in_(created_user_id))

    if created_start and created_end:
        query = query.filter(Machine2Jobgroup.created.between(created_start, created_end))
        
    elif created_start and (created_end is None):
        query = query.filter(created_start <= Machine2Jobgroup.created)
        
    elif (not created_start) and created_end:
        query = query.filter(Machine2Jobgroup.created <= created_end)
        
    if desc is True:
        return query.order_by(Machine2Jobgroup.id.desc()).all()
    else:
        return query.order_by(Machine2Jobgroup.id.asc()).all()


def findbyhost(session, host_id, created_start=None,
              created_end=None, created_user_id=None, desc=False):

    query = session.query(Machine).add_entity(Machine2Jobgroup).join(Machine2Jobgroup)

    query = query.filter(
                or_(
                    and_(Machine.parent_id == host_id, Machine.attribute == MACHINE_ATTRIBUTE['GUEST']),
                    and_(Machine.id == host_id, Machine.attribute == MACHINE_ATTRIBUTE['HOST'])
                )
            )

    #if created_user_id:
    if not created_user_id is None:
        query = query.filter(Machine2Jobgroup.created_user_id.in_(created_user_id))

    if created_start and created_end:
        query = query.filter(Machine2Jobgroup.created.between(created_start, created_end))
        
    elif created_start and (created_end is None):
        query = query.filter(created_start <= Machine2Jobgroup.created)
        
    elif (not created_start) and created_end:
        query = query.filter(Machine2Jobgroup.created <= created_end)
        
    if desc is True:
        return query.order_by(Machine2Jobgroup.id.desc()).all()
    else:
        return query.order_by(Machine2Jobgroup.id.asc()).all()

def findbyguest(session, guest_id, created_start=None,
              created_end=None, created_user_id=None, desc=False):

    query = session.query(Machine).add_entity(Machine2Jobgroup).join(Machine2Jobgroup)

    query = query.filter(
        Machine.id == guest_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST'])

    #if created_user_id:
    if not created_user_id is None:
        query = query.filter(Machine2Jobgroup.created_user_id.in_(created_user_id))

    if created_start and created_end:
        query = query.filter(Machine2Jobgroup.created.between(created_start, created_end))
        
    elif created_start and (created_end is None):
        query = query.filter(created_start <= Machine2Jobgroup.created)
        
    elif (not created_start) and created_end:
        query = query.filter(Machine2Jobgroup.created <= created_end)
        
    if desc is True:
        return query.order_by(Machine2Jobgroup.id.desc()).all()
    else:
        return query.order_by(Machine2Jobgroup.id.asc()).all()


def findbyjobgroup_id1(session, jobgroup_id):
    if jobgroup_id:
        query = session.query(Machine).add_entity(Machine2Jobgroup).join(Machine2Jobgroup)
        query = query.filter(Machine2Jobgroup.jobgroup_id == jobgroup_id)
        return query.first()
    else:
        return None

def findbyjobgroupor(session, jobgroup_ids, desc=False):
    if jobgroup_ids:
        query = session.query(Machine).add_entity(
            Machine2Jobgroup).join(
            Machine2Jobgroup)
        
        jg_id_list = jobgroup_ids.split()
        or_clause = or_()
        for id in jg_id_list:
            or_clause.append(Machine2Jobgroup.jobgroup_id.like("%"+id+"%"))

        if desc is True:
            return query.filter(or_clause).order_by(
                Machine2Jobgroup.jobgroup_id.desc()).all()
        else:
            return query.filter(or_clause).order_by(
                Machine2Jobgroup.jobgroup_id.asc()).all()
    else:
        return None
