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

import sqlalchemy
from sqlalchemy.orm import mapper, clear_mappers, relation
import karesansui
import karesansui.db.model
from karesansui.lib.const import DEFAULT_LANGS

def get_option_table(metadata, now):
    """<comment-ja>
    Option のテーブル定義を返却します。
    @param metadata: MetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    @return: sqlalchemy.schema.Table
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return sqlalchemy.Table('option', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('created_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('modified_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('key', sqlalchemy.String(12),
                                              nullable=False,
                                              unique=True,
                                              ),
                            sqlalchemy.Column('value', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),
                            )

class Option(karesansui.db.model.Model):
    """<comment-ja>
    Optionテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, created_user, modified_user,
                 key, value=None):
        """<comment-ja>
        @param created_user: 作成者
        @type created_user: User
        @param modified_user: 最終更新者
        @type modified_user: User
        @param key: option key
        @type key: str
        @param value: option value
        @type value: str(Text)
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.created_user = created_user
        self.modified_user = modified_user
        self.key = key
        self.value = value

    def get_json(self, languages):
        ret = {}
        ret["id"] = self.id

        ret["key"] = self.key
        ret["value"] = self.value

        ret["created_user_id"] = self.created_user_id
        ret["created_user"] = self.created_user.get_json(languages)

        ret["modified_user_id"] = self.modified_user_id
        ret["modified_user"] = self.modified_user.get_json(languages)

        ret["created"] = self.created.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        ret["modified"] = self.modified.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])

        return ret
    
    def __repr__(self):
        return "Option<'key=%s, value=%s>" \
               % (self.key, self.value)

def reload_mapper(metadata, now):
    """<comment-ja>
    Option(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_option = get_option_table(metadata, now)
    t_user = metadata.tables['user']

    mapper(Option, t_option, properties={
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_option.c.created_user_id==t_user.c.id),
        'modified_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_option.c.modified_user_id==t_user.c.id),
        })

if __name__ == '__main__':
    import sqlalchemy.orm
    bind_name = 'sqlite:///:memory:'
    engine = sqlalchemy.create_engine(bind_name,
                                      encoding="utf-8",
                                      convert_unicode=True,
                                      #assert_unicode='warn', # DEBUG
                                      echo=True,
                                      echo_pool=False
                                      )   
       
    metadata = sqlalchemy.MetaData(bind=engine)
    if metadata.bind.name == 'sqlite':
        _now = sqlalchemy.func.datetime('now', 'localtime')
    else:
        _now = sqlalchemy.func.now()
                            
    reload_mapper(metadata, _now)
    import pdb; pdb.set_trace()
    
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # INSERT
    # SELECT One
    # UPDATE
    # DELETE
