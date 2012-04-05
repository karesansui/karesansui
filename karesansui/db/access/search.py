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

from sqlalchemy import and_, or_

from karesansui.lib.utils import detect_encoding

def findbyand(session, query, model, attr, desc=False):
    """
    <comment-ja>
    指定したテーブルとテーブル属性で、
    指定した検索文字列でAND検索を行い、
    検索結果を返却します。

    @param session: セッション
    @param query: 検索文字列のリスト
    @param model: 検索するテーブルのオブジェクト
    @param attr: 検索するテーブル属性のオブジェクト
    @return: 検索結果のリスト
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    query = query.split()

    and_clause = and_()
    for q in query:
        #q = unicode(q, detect_encoding(q))
        or_clause = or_()
        for a in attr:
            or_clause.append(a.like("%"+q+"%"))
        and_clause.append(or_clause)
    
    if desc is True:
        return session.query(model).filter(and_clause).order_by(model.id.desc()).all()
    else:
        return session.query(model).filter(and_clause).order_by(model.id.asc()).all()

def findbyor(session, query, model, attrs, desc=False):
    or_clause = or_()
    for x in attrs:
        or_clause.append(x.like("%"+query+"%"))

    if desc is True:
        return session.query(model).filter(or_clause).order_by(model.id.desc()).all()
    else:
        return session.query(model).filter(or_clause).order_by(model.id.asc()).all()
