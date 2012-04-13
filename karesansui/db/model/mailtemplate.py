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
import karesansui.db.model.machine
from karesansui.lib.const import DEFAULT_LANGS

def get_mailtemplate_table(metadata, now):
    """<comment-ja>
    メールテンプレート(Mailtemplate)のテーブル定義を返却します。
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
    return sqlalchemy.Table('mailtemplate', metadata,
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
                            sqlalchemy.Column('name', sqlalchemy.String(256),
                                              nullable=False,
                                              unique=True,
                                              ),
                            sqlalchemy.Column('encoding', sqlalchemy.String(12),
                                              nullable=False,
                                              default='ascii'
                                              ),
                            sqlalchemy.Column('mail_to', sqlalchemy.Text,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('mail_from', sqlalchemy.Text,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('mail', sqlalchemy.Text,
                                              nullable=False,
                                              ),
                            # 256(FQDN) + 1(":") + 5(65535) = 262
                            sqlalchemy.Column('mta', sqlalchemy.String(262),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('cc', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('bcc', sqlalchemy.Text,
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

class Mailtemplate(karesansui.db.model.Model):
    """<comment-ja>
    MailTemplateテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, created_user, modified_user,
                 name, mail_to, mail_from, mail, mta,
                 cc=None, bcc=None, encoding=None):
        """<comment-ja>
        @param created_user: 作成者
        @type created_user: User
        @param modified_user: 最終更新者
        @type modified_user: User
        @param name: メールテンプレート名
        @type name: str
        @param mail_to: 宛先メールアドレス
        @type mail_to: str
        @param mail_from: 差出人メールアドレス
        @type mail_from: str
        @param mail: 本文
        @type mail: str
        @param mta: SMTPサーバー
        @type mta: str
        @param cc: Cc
        @type cc: str
        @param bcc: Bcc
        @type bcc: str
        @param encoding: Encoding
        @type encoding: str
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.created_user = created_user
        self.modified_user = modified_user
        self.name = name
        self.mail_to = mail_to
        self.mail_from = mail_from
        self.mail = mail
        self.mta = mta
        self.cc = cc
        self.bcc = bcc
        self.encoding = encoding

    def get_json(self, languages):
        ret = {}
        ret["id"] = self.id

        ret["name"] = self.name
        ret["mail_to"] = self.mail_to
        ret["mail_from"] = self.mail_from
        ret["mail"] = self.mail
        ret["mta"] = self.mta
        ret["cc"] = self.cc
        ret["bcc"] = self.bcc
        ret["encoding"] = self.encoding

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
        return "MailTemplate<'%s, from=%s, to=%s'>" \
               % (self.name, self.mail_from, self.mail_to)

def reload_mapper(metadata, now):
    """<comment-ja>
    MailTemplate(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_mailtemplate = get_mailtemplate_table(metadata, now)
    t_user = metadata.tables['user']

    mapper(Mailtemplate, t_mailtemplate, properties={
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_mailtemplate.c.created_user_id==t_user.c.id),
        'modified_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_mailtemplate.c.modified_user_id==t_user.c.id),
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
