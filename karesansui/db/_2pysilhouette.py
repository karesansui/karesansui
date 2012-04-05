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

import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, mapper, scoped_session
from sqlalchemy.pool import SingletonThreadPool, QueuePool

import karesansui

from pysilhouette.db.model import *
from pysilhouette.db import Database

# private
__db = None
#__engine = None
#__metadata = None


# function
def get_engine():
    """<comment-ja>
    Databaseを返却します。(Optimistic Singleton)
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    global __db
    if __db is None:
        logger = logging.getLogger("karesansui.pysilhouette.db.engine")
        echo = True
        echo_pool = True

        if karesansui.sheconf['database.url'][:6].strip() == 'sqlite':
            __db = Database(karesansui.sheconf['database.url'],
                          encoding="utf-8",
                          convert_unicode=True,
                          #assert_unicode='warn', # DEBUG
                          echo = echo,
                          echo_pool = echo_pool,
                          )
        else:
            if int(karesansui.sheconf['database.pool.status']) == 0:
                __db = Database(karesansui.sheconf['database.url'],
                              encoding="utf-8",
                              convert_unicode=True,
                              #assert_unicode='warn', # DEBUG
                              poolclass=SingletonThreadPool,
                              #echo = opts.verbose,
                              #echo_pool = opts.verbose,
                              echo=echo,
                              echo_pool=echo_pool
                              )
            else:
                __db = Database(karesansui.sheconf['database.url'],
                              encoding="utf-8",
                              convert_unicode=True,
                              #assert_unicode='warn', # DEBUG
                              poolclass=QueuePool,
                              pool_size=int(karesansui.sheconf['database.pool.size']),
                              max_overflow=int(karesansui.sheconf['database.pool.max.overflow']),
                              #echo = opts.verbose,
                              #echo_pool = opts.verbose,
                              echo=echo,
                              echo_pool=echo_pool
                              )

        __engine = __db.get_engine()

        # mapper!!
        mapper(__db.get_metadata())

        logger.debug('[pysilhouette] engine.name=%s - pool=%s' % (__engine.name, __engine.pool.__class__))
    return __db.get_engine()


def get_metadata(engine=None):
    """<comment-ja>
    Pysilhouetteのメタデータを取得します。
    @param engine: データベースエンジン
    @type engine: SQLAlchemy#Engine
    @rtype: SQLAlchemy#MetaData
    @return: メタデータ
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    global __db
    if __db is None:
        engine = get_engine()
    # mapper!! 
    return __db.get_metadata()    

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
    # thread-local Customize!
    #return sessionmaker(bind=get_engine(), autoflush=False)
    return scoped_session(
        sessionmaker(bind=get_engine(), autoflush=False))

if __name__ == '__main__':
    pass
