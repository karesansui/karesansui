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
from karesansui.db.model.machine import Machine
from karesansui.db.access import dbsave, dbupdate, dbdelete

# -- all
def findbyall(session, is_deleted=False):
    return session.query(Machine).filter(
        Machine.is_deleted == is_deleted).all()

def findby1(session, machine_id, is_deleted=False):
    return session.query(Machine).filter(
        Machine.id == machine_id).filter(
        Machine.is_deleted == is_deleted).first()

def findby1name(session, machine_name, is_deleted=False):
    return session.query(Machine).filter(
        Machine.name == machine_name).filter(
        Machine.is_deleted == is_deleted).first()

def findbyalluniquekey(session, uniq_key):
    return session.query(Machine).filter(
        Machine.uniq_key == uniq_key).all()

def findby1uniquekey(session, uniq_key, is_deleted = False):
    return session.query(Machine).filter(
        Machine.uniq_key == uniq_key).filter(
        Machine.is_deleted == is_deleted).first()

def findby1hostname(session, hostname, is_deleted=False):
    return session.query(Machine).filter(
        Machine.hostname == hostname).filter(
        Machine.is_deleted == is_deleted).first()

# -- host
def findbyhostall(session, is_deleted=False):
    return session.query(Machine).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['HOST']).filter(
        Machine.is_deleted == is_deleted).all()

def findbyhost1(session, machine_id, is_deleted=False):
    return session.query(Machine).filter(
        Machine.id == machine_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['HOST']).filter(
        Machine.is_deleted == is_deleted).first()

def is_findbyhost1(session, machine_id, is_deleted=False):
    """<comment-ja>
    指定したホストレコードが存在するか。
     - 0 : 存在しない
     - 1 : 存在する
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    return session.query(Machine).filter(
        Machine.id == machine_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['HOST']).filter(
        Machine.is_deleted == is_deleted).count()


# -- guest
def findbyhost1guestall(session, host_id, is_deleted=False):
    return session.query(Machine).filter(
        Machine.parent_id == host_id).filter( 
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST']).filter(
        Machine.is_deleted == is_deleted).all()

def findbyguestall(session, is_deleted=False):
    return session.query(Machine).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST']).filter(
        Machine.is_deleted == is_deleted).all()

def findbyguest1(session, guest_id, is_deleted=False):
    return session.query(Machine).filter(
        Machine.id == guest_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST']).filter(
        Machine.is_deleted == is_deleted).first()

def is_findbyguest1(session, guest_id, host_id=None, is_deleted=False):
    """<comment-ja>
    指定したゲストレコードが存在するか。
     - 0 : 存在しない
     - 1 : 存在する
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    query = session.query(Machine).filter(
        Machine.id == guest_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST']).filter(
        Machine.is_deleted == is_deleted)
    if host_id:
        query.filter(Machine.parent_id == host_id)

    return query.count()

# custom
def deleteby1uniquekey(session, uniq_key, is_deleted=False):
    guest = session.query(Machine).filter(
        Machine.uniq_key == uniq_key).one()

    return logical_delete(session, guest)

@dbupdate
def logical_delete(session, machine):
    if machine.attribute == MACHINE_ATTRIBUTE['HOST']:
        machine.hostname = None

    machine.is_deleted = True
    return session.update(machine)

@dbsave
def save(session, machine):
    session.save(machine)

@dbupdate
def update(session, machine):
    session.update(machine)
    
@dbdelete
def delete(session, machine):
    session.delete(machine)

# new instance
new = Machine
