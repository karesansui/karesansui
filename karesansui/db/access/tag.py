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
from karesansui.db.model.tag import Tag
from karesansui.db.model.machine import Machine
from karesansui.db.access import dbsave, dbupdate, dbdelete
from karesansui.db.access.search import findbyand as _findbyand

# -- all
def findbyall(session):
    """<comment-ja>
    すべてのタグ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @rtype: karesansui.db.model.tag.Tag
    @return: Tag Class
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return session.query(Tag).all()

def findby1(session, tag_id):
    """<comment-ja>
    タグIDを元にタグ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param tag_id: Tag ID
    @type tag_id: int
    @rtype: karesansui.db.model.tag.Tag
    @return: Tag Class    
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if tag_id:
        return session.query(Tag).filter(Tag.id == tag_id).first()
    else:
        return None

def findby1name(session, tag_name):
    """<comment-ja>
    タグ名を指定して1件のタグ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param tag_name: タグ名条件
    @type tag_name: string
    @return: karesansui.db.model.tag.Tag
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if tag_name:
        return session.query(Tag).filter(Tag.name == tag_name).first()
    else:
        return None

def findbyand(session, query):
    """<comment-ja>
    クエリー条件のAND検索で、多数のユーザ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param query: クエリー条件
    @type query: list
    @return: karesansui.db.model.user.User
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return _findbyand(session, query, Tag, [Tag.name])

# -- host
def findbyhostall(session, is_deleted=False):
    return session.query(Tag).join("machine").filter(
        Machine.attribute == MACHINE_ATTRIBUTE['HOST']).filter(
        Machine.is_deleted == is_deleted).all()

# -- guest
def findbyhost1guestall(session, host_id, is_deleted=False):
    return session.query(Tag).join("machine").filter(
        Machine.parent_id == host_id).filter(
        Machine.attribute == MACHINE_ATTRIBUTE['GUEST']).filter(
        Machine.is_deleted == is_deleted).all()

def samecount(session, tag_name):
    return session.query(Tag).filter(Tag.name == tag_name).count()

@dbsave
def save(session, tag):
    session.add(tag)

@dbupdate
def update(session, tag):
    session.add(tag)
    
@dbdelete
def delete(session, tag):
    session.delete(tag)

def new(name = None):
    return Tag(name) 
    

# new instance
new = Tag
