#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import sqlalchemy
import sqlalchemy.orm
from pysilhouette.db.model import *
import sqlalchemy.pool
import sqlite

bind_name = 'sqlite:///:memory:'

def gs():
    hoge = ':memory:'
    return sqlite.connect('/tmp/hoge.db')

def main():
    #qp = sqlalchemy.pool.QueuePool( gs , pool_size=5, max_overflow=100, echo=True)
    #engine = sqlalchemy.create_engine(bind_name, encoding="utf8", echo=True, pool=qp)
    #engine = sqlalchemy.create_engine(bind_name, encoding="utf8", echo=True, poolclass=sqlalchemy.pool.QueuePool)
    
    engine = sqlalchemy.create_engine(bind_name, encoding="utf8", echo=True)
    
    metadata = sqlalchemy.MetaData(bind=engine)
    
    t_job_group = get_job_group_table(metadata)
    t_job = get_job_table(metadata)

    sqlalchemy.orm.mapper(JobGroup, t_job_group, properties={'jobs': sqlalchemy.orm.relation(Job)})
    sqlalchemy.orm.mapper(Job, t_job)
    
    metadata.drop_all()
    metadata.create_all()
    
    Session = sqlalchemy.orm.sessionmaker(engine)
    session1 = Session()
    session2 = Session()
    session3 = Session()
    hoge = session1.query(JobGroup).all()
    jg1 = JobGroup(u'Test Success', '')
    jg1.jobs.append(Job(u'日付取得','0','/bin/date', 'fdaf'))
    session1.add(jg1)
    session1.close()
                                        
if __name__ == '__main__':
    main()
