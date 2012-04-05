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

from sqlalchemy.orm.exc import NoResultFound

from karesansui.lib.crypt import sha1compare
from karesansui.db.model.user import User
from karesansui.db.access import dbsave, dbupdate, dbdelete
from karesansui.db.access.search import findbyand as _findbyand

from karesansui import KaresansuiDBException

def findbyall(session):
    """<comment-ja>
    ユーザを全て取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return session.query(User).all()

def findby1(session, id):
    """<comment-ja>
    ユーザIDを指定して1件のユーザ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param id: ユーザID
    @type id: int
    @return: karesansui.db.model.user.User
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return session.query(User).filter(User.id == id).first()

# -- email
def findby1email(session, email):
    """<comment-ja>
    メールアドレスを指定して1件のユーザ情報を取得します
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param email: メールアドレス
    @type email: str
    @return: karesansui.db.model.user.User
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return session.query(User).filter(User.email == email).first()

def findbyname_BM(session, nickname):
    """<comment-ja>
    ニックネームを部分一致で検索します。
    @param
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return session.query(User).filter(User.nickname.like("%%%s%%" % nickname)).all()
    

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
    return _findbyand(session, query, User, [User.nickname, User.email])

@dbsave
def save(session, user):
    session.save(user)

@dbupdate
def update(session, user):
    session.update(user)
    
@dbdelete
def delete(session, user):
    session.delete(user)

def new(email, password, salt, nickname, languages=None):
    return User(email, password, salt, nickname, languages)

# -- process method
def login(session, email, password):
    """<comment-ja>
    ログイン情報からユーザ情報を取得します。
    @param session: Session
    @type session: sqlalchemy.orm.session.Session
    @param email: e-mail
    @type email: str
    @param password: パスワード
    @type password: str
    @return: karesansui.db.model.user.User
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if email and password:
        _r = session.query(User).filter(User.email == email).first()
        if _r is None:
            return None

        if sha1compare(_r.password, password, _r.salt) is True:
            return _r
        else:
            return None
    return None

if __name__ == '__main__':
    import sqlalchemy.orm
    from karesansui.db.model.user import User, get_user_table
    bind_name = 'sqlite:///:memory:'
    engine = sqlalchemy.create_engine(bind_name, encoding="utf8", echo=True)
    metadata = sqlalchemy.MetaData(bind=engine)
    t_user = get_user_table(metadata)
    sqlalchemy.orm.mapper(User, t_user)
    #metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()
    # --
    """
    u = User('pass', 'hoge@example.com', 'karesansui', 'ja-JP')
    save(session, u)
    ua = findbyall(session)
    print ua    
    u = findby1(session, ua[0].id)
    print u
    u.password = 'update password'
    update(session, u)
    u = findby1(session, ua[0].id)
    print u
    delete(session, u)
    u = findbyall(session)
    print u
    """
    # process method
    u = User('pass', 'hoge@example.com', 'karesansui', 'ja-JP')
    if save(session, u):
        u = login(session, 'karesansui', 'pass')
        print u
