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
        try:
            ret["created"] = self.created.strftime(
                DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        except:
            ret["created"] = "unknown"
        try:
            ret["modified"] = self.modified.strftime(
                DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        except:
            ret["modified"] = "unknown"
        
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
    session.add(_m_u)
    session.commit()
    # SELECT One
    u = session.query(User).filter(User.email == u'hoge@localhost').one()
    
    print _m_u.__repr__()
    # UPDATE
    _m_u.email = u'foo@localhost'
    session.add(_m_u)
    session.commit()
    # DELETE
    _m_u = session.query(User).filter(User.email == u'foo@localhost').one()
    session.delete(_m_u)
    session.commit()
