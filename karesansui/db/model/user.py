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

import sqlalchemy
from sqlalchemy.orm import mapper, clear_mappers

import karesansui
import karesansui.db.model
from karesansui.lib.const import DEFAULT_LANGS

def get_user_table(metadata, now):
    """<comment-ja>
    ユーザ(User)のテーブル定義を返却します。
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
    return sqlalchemy.Table('user', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('email', sqlalchemy.String(256),
                                              unique=True,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('password', sqlalchemy.String(40),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('salt', sqlalchemy.Unicode(16),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('nickname', sqlalchemy.Unicode(16),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('languages', sqlalchemy.Unicode(6),
                                              default=u'ja_JP',
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),
                            )

class User(karesansui.db.model.Model):
    """<comment-ja>
    ユーザテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, email, password, salt, nickname, languages=None):
        """<comment-ja>
        @param email: E-mail
        @type email: str
        @param password: パスワード
        @type password: str
        @param salt: salt
        @type salt: str
        @param nickname: ニックネーム
        @type nickname: str
        @param languages: 言語
        @type languages str
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.password = password
        self.salt = salt
        self.email = email
        self.nickname = nickname
        self.languages = languages

    def get_json(self, languages):
        ret = {}
        ret["id"] = self.id 
        ret["email"] = self.email
        #ret["password"] = self.password
        #ret["salt"] = self.salt
        ret["nickname"] = self.nickname
        ret["languages"] = self.languages
        ret["created"] = self.created.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        ret["modified"] = self.modified.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        
        return ret
    
    def __repr__(self):
        return "User<'%s, %s'>" % (
            self.email, self.languages)

def reload_mapper(metadata, now):
    """<comment-ja>
    User(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_user = get_user_table(metadata, now)
    mapper(User, t_user)

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
    reload_mapper(metadata)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # INSERT
    from karesansui.lib.crypt import sha1encrypt
    (password, salt) = sha1encrypt(u'password')
    from karesansui.lib.utils import uni_force
    _m_u = User(u'hoge@localhost', uni_force(password), unicode(salt, 'utf-8'), u'ja', u'ja_JP')
    session.save(_m_u)
    session.commit()
    # SELECT One
    u = session.query(User).filter(User.email == u'hoge@localhost').one()
    
    print _m_u.__repr__()
    # UPDATE
    _m_u.email = u'foo@localhost'
    session.update(_m_u)
    session.commit()
    # DELETE
    _m_u = session.query(User).filter(User.email == u'foo@localhost').one()
    session.delete(_m_u)
    session.commit()
