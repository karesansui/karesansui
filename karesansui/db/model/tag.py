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
from sqlalchemy.orm import mapper, clear_mappers, relation
import karesansui
import karesansui.db.model
from karesansui.lib.const import DEFAULT_LANGS  

def get_tag_table(metadata, now):
    """<comment-ja>
    タグ(Tag)のテーブル定義を返却します。
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
    return sqlalchemy.Table('tag', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
#                            sqlalchemy.Column('notebook_id', sqlalchemy.Integer,
#                                              sqlalchemy.ForeignKey('notebook.id'),
#                                              ),
                            sqlalchemy.Column('name', sqlalchemy.String(24),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),

                            )

class Tag(karesansui.db.model.Model):
    """<comment-ja>
    tagテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
#    def __init__(self, name, notebook):
    def __init__(self, name):
        """<comment-ja>
        @param name: タグ名
        @type name: str
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.name = name
#        self.notebook = notebook

    def get_json(self, languages):
        ret = {} 
        ret["id"] = self.id
#        ret["notebook_id"] = self.notebook_id
        ret["name"] = self. name
        ret["created"] = self.created.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        ret["modified"] = self.modified.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        
        return ret
      
    def __repr__(self):
        return "Tag<'%s'>" % (self.name)

def reload_mapper(metadata, now):
    """<comment-ja>
    Tag(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_tag = get_tag_table(metadata, now)
    mapper(Tag, t_tag, properties={
#        'notebook' : relation(karesansui.db.model.notebook.Notebook),
    })

if __name__ == '__main__':
    import sqlalchemy.orm
    bind_name = 'sqlite:///:memory:'
    engine = sqlalchemy.create_engine(bind_name,
                                      encoding="utf-8",
                                      convert_unicode=True,
                                      #assert_unicode='warn', #DEBUG
                                      echo=True,
                                      echo_pool=False
                                      )   
    
    metadata = sqlalchemy.MetaData(bind=engine)
    # relation
#    karesansui.db.model.notebook.reload_mapper(metadata)
    reload_mapper(metadata)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # INSERT
    # SELECT One
    # UPDATE
    # DELETE
