#! /usr/bin/env python
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

import logging

from sqlalchemy.orm.exc import UnmappedInstanceError

from karesansui import KaresansuiDBException

from karesansui.lib.utils import get_model_name

def dbsave(func):
    """<comment-ja>
    INSERT文の成否の返却とエラー処理を行うデコレータ。
    INSERT文が成功していれば、前回のCOMMIT後から挿入した行数が返却される。
    INSERT文が失敗していれば、0が返却される。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('karesansui.db.access')
        session = args[0]
        model = args[1]
        model_name = get_model_name(model)
        model_id = model.id  # If you do not flush the session, Unable to retrieve the model id.
        try:
            func(*args, **kwargs)
        except UnmappedInstanceError as ui:
            logger.error(('Data to insert is failed, '
                          'Invalid value was inputed. '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))
            raise KaresansuiDBException(('Data to insert is failed, '
                          'Invalid value was inputed. '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))

        num = len(session.new)
        if not num:
            logger.warn('Data has not been changed. - %s=%s' %  (model_name, model_id))
            return num  # The return value assume zero
        
        logger.debug('Data to insert is succeeded. - %s=%s' % (model_name, model_id))
        return num
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def dbupdate(func):
    """<comment-ja>
    UPDATE文の成否の返却とエラー処理を行うデコレータ。
    UPDATE文が成功していれば、前回のCOMMIT後から更新した行数が返却される。
    UPDATE文が失敗していれば、0が返却される。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('karesansui.db.access')
        session = args[0]
        model = args[1]
        model_name = get_model_name(model)
        model_id = model.id
        try:
            func(*args, **kwargs)
        except UnmappedInstanceError as ui:
            logger.error(('Data to update is failed, '
                          'Invalid value was inputed '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))
            raise KaresansuiDBException(('Data to update is failed, '
                          'Invalid value was inputed. '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))
        
        num = len(session.dirty)
        if not num:
            logger.warn('Data has not been changed. - %s=%s' %  (model_name, model_id))
            return num  # The return value assume zero
        
        logger.debug('Data to update is succeeded. - %s=%s' % (model_name, model_id))
        return num
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def dbdelete(func):
    """<comment-ja>
    DELETE文の成否の返却とエラー処理を行うデコレータ。
    DELETE文が成功していれば、前回のCOMMIT後から削除された行数が返却される。
    DELETE文が失敗していれば、0が返却される。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('karesansui.db.access')
        session = args[0]
        model = args[1]
        model_name = get_model_name(model)
        model_id = model.id
        try:
            func(*args, **kwargs)
        except UnmappedInstanceError as ui:
            logger.error(('Data to delete is failed, '
                          'Invalid value was inputed '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))
            raise KaresansuiDBException(('Data to delete is failed, '
                          'Invalid value was inputed. '
                          '- %s=%s, error=%s') % (model_name, model_id, ''.join(ui)))

        num = len(session.deleted)
        if not num:
            logger.warn('Data has not been changed. - %s=%s' %  (model_name, model_id))
            return num  # The return value assume zero
        
        logger.debug('Data to delete is succeeded. - %s=%s' % (model_name, model_id))
        return num
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

if __name__ == '__main__':
    import sqlalchemy.orm
    from karesansui.db.model.user import User, get_user_table

    @dbsave
    def save(session, user):
        session.add(user)

    @dbupdate
    def update(session, user):
        session.add(user)

    @dbdelete
    def delete(session, user):
        session.delete(user)

    bind_name = 'sqlite:///:memory:'
    engine = sqlalchemy.create_engine(bind_name, encoding="utf8")
    metadata = sqlalchemy.MetaData(bind=engine)
    t_user = get_user_table(metadata)
    sqlalchemy.orm.mapper(User, t_user)
    #metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()
    # --
    # insert
    u = User('hoge@example.com', 'pass', 'salt', 'karesansui', 'ja-JP')  
    try:
        ret = save(session, u)
    except KaresansuiDBException as kdae:
        print(kdae)
    session.commit()
    hoge = session.query(User).filter(User.email == "hoge@example.com").first()
    print(hoge, ret)

    # update
    hoge = session.query(User).filter(User.email == "hoge@example.com").first()
    hoge.email = 'karesansui@example.com'
    try:
        ret = update(session, hoge)
    except KaresansuiDBException as kdae:
        print(kdae)
    session.commit()
    kare = session.query(User).filter(User.email == "karesansui@example.com").first()
    print(kare, ret)

    # delete 
    kare = session.query(User).filter(User.email == "karesansui@example.com").first()
    try:
        ret = delete(session, kare)
    except KaresansuiDBException as kdae:
        print(kdae)
    session.commit()
    kare = session.query(User).filter(User.email == "karesansui@example.com").first()
    print(kare, ret)
