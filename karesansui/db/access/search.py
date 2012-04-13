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
