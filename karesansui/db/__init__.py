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

import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, mapper, scoped_session
from sqlalchemy.pool import SingletonThreadPool, QueuePool

import karesansui
from karesansui.db.model import reload_mappers

#: SQLAlchemy#Engine
__engine = None

# function
def get_engine():
    """<comment-ja>
    Databaseを返却します。(Optimistic Singleton)
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    global __engine
    if __engine is None:
        logger = logging.getLogger('karesansui.db.engine')
        echo = True
        echo_pool = True
        if karesansui.config['database.bind'][:6].strip() == 'sqlite':
            engine = create_engine(karesansui.config['database.bind']+'?check_same_thread=False',
                                   encoding="utf-8",
                                   convert_unicode=True,
                                   #assert_unicode='warn', # DEBUG
                                   echo=echo,
                                   echo_pool=echo_pool,
                                   )

        else:
            if int(karesansui.config['database.pool.status']) == 1:
                engine = create_engine(karesansui.config['database.bind'],
                                       encoding="utf-8",
                                       convert_unicode=True,
                                       #assert_unicode='warn', # DEBUG
                                       poolclass=QueuePool,
                                       pool_size=int(karesansui.config['database.pool.size']),
                                       max_overflow=int(karesansui.config['database.pool.max.overflow']),
                                       echo=echo,
                                       echo_pool=echo_pool,
                                       )
            else:
                engine = create_engine(karesansui.config['database.bind'],
                                       encoding="utf-8",
                                       convert_unicode=True,
                                       #assert_unicode='warn', # DEBUG
                                       poolclass=SingletonThreadPool,
                                       echo=echo,
                                       echo_pool=echo_pool,
                                       )
        logger.debug('[karesansui] engine.name=%s - pool=%s' % (engine.name, engine.pool.__class__))

        # MataData mapper!!
        get_metadata(engine)
        __engine = engine

    return __engine

#: SQLAlchemy#MetaData
__metadata = None

def get_metadata(engine=None):
    """<comment-ja>
    Karesansuiのメタデータを取得します。
    @param engine: データベースエンジン
    @type engine: SQLAlchemy#Engine
    @rtype: SQLAlchemy#MetaData
    @return メタデータ
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    global __metadata
    if engine is None:
        engine = get_engine()
    if __metadata is None:
        __metadata = MetaData(engine)
        mapper(__metadata)
    return __metadata

def mapper(metadata):
    """<comment-ja>
    関連するテーブル情報等々をマッピングします。
    @param metadata: メタデータ
    @type metadata: SQLAlchemy#MetaData
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    reload_mappers(metadata)

def get_session():
    """<comment-ja>
    thread-localでセッションを取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return scoped_session(
        sessionmaker(bind=get_engine(), autoflush=False))


if __name__ == '__main__':
    pass
