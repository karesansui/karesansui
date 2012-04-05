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
import karesansui.db.model

def get_machine2tag_table(metadata, now):
    """<comment-ja>
    Machine2tagのテーブル定義を返却します。
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
    return sqlalchemy.Table('machine2tag', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('tag_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('tag.id'),
                                              ),
                            sqlalchemy.Column('machine_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('machine.id'),
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),
                            )

class Machine2Tag(karesansui.db.model.Model):
    """<comment-ja>
    machine2tagテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, tag_id, machine_id):
        """<comment-ja>
        @param tag_id: タグID
        @type tag_id: int
        @param machine_id: マシンID
        @type machine_id: int
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.tag_id = tag_id
        self.machine_id = machine_id

    def __repr__(self):
        return "Machine2tag<'%d, %s, %s'>" % (self.id, self.tag_id, self.machine_id)

def reload_mapper(metadata, now):
    """<comment-ja>
    machine2tag(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_machine2tag = get_machine2tag_table(metadata, now)

if __name__ == '__main__':
    import sqlalchemy.orm
    bind_name = 'sqlite:///:memory:'
    engine = sqlalchemy.create_engine(bind_name,
                                      encoding="utf-8",
                                      convert_unicode=True,
                                      #assert_unicode='warn', #DEBUG
                                      echo=True,
                                      echo_pool=True
                                      )
    
    metadata = sqlalchemy.MetaData(bind=engine)
    t_machine = get_machine_table(metadata)
    sqlalchemy.orm.mapper(Machine, t_machine)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # INSERT
    # SELECT One
    # UPDATE
    # DELETE

