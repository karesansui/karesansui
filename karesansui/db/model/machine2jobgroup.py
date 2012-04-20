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
from sqlalchemy.orm import mapper, clear_mappers, relation
import karesansui.db.model
import karesansui.db.model.user
import karesansui.db.model.machine

def get_machine2jobgroup_table(metadata, now):
    """<comment-ja>
    (Machine2jobgroup)のテーブル定義を返却します。
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
    return sqlalchemy.Table('machine2jobgroup', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('machine_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('machine.id'),
                                              ),
                            sqlalchemy.Column('jobgroup_id', sqlalchemy.Integer,
                                              nullable=False,
                                              ),
                            # PySilhouette 
                            sqlalchemy.Column('uniq_key', sqlalchemy.Unicode(36),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('created_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'), 
                                              ),
                            sqlalchemy.Column('modified_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'), 
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),
                            )

class Machine2Jobgroup(karesansui.db.model.Model):
    """<comment-ja>
    machine2jobgroupテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, machine, jobgroup_id, uniq_key, created_user, modified_user):
        """<comment-ja>
        @param machine_id: マシン
        @type machine_id: Machine
        @param jobgroup_id : ジョブグループID
        @type jobgroup_id: int
        @param uniq_key: ユニークキー PySilhouette
        @type uniq_key: str
        @param created_user_id: 作成者
        @type created_user_id: User
        @param created_user_id: 最終更新者
        @type created_user_id: User
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.machine = machine
        self.jobgroup_id = jobgroup_id
        self.uniq_key = uniq_key
        self.created_user = created_user
        self.modified_user = modified_user
        
    def __repr__(self):
        return "Machine2Jobgroup<'%d, %d, %s'>" % (self.machine.id, self.jobgroup_id, self.uniq_key)

def reload_mapper(metadata, now):
    """<comment-ja>
    Machine2Jobgroup(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_machine2jobgroup = get_machine2jobgroup_table(metadata, now)
    t_machine = metadata.tables["machine"]
    t_user = metadata.tables["user"]
    mapper(Machine2Jobgroup, t_machine2jobgroup, properties={
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_machine2jobgroup.c.created_user_id==t_user.c.id),
        
        'modified_user' : relation(karesansui.db.model.user.User,
                                   primaryjoin=t_machine2jobgroup.c.modified_user_id==t_user.c.id),
        
        'machine' : relation(karesansui.db.model.machine.Machine,
                             primaryjoin=t_machine2jobgroup.c.machine_id==t_machine.c.id,
                             ),
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
    # relation
    karesansui.db.model.machine.reload_mapper(metadata)
    karesansui.db.model.notebook.reload_mapper(metadata)
    karesansui.db.model.user.reload_mapper(metadata)
    karesansui.db.model.tag.reload_mapper(metadata)

    reload_mapper(metadata)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # INSERT
    # SELECT One
    # UPDATE
    # DELETE
