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
from sqlalchemy.orm import mapper, clear_mappers, relation, backref
import karesansui
import karesansui.db.model
import karesansui.db.model.notebook
import karesansui.db.model.machine
import karesansui.db.model.user
from karesansui.lib.const import DEFAULT_LANGS

def get_snapshot_table(metadata, now):
    """<comment-ja>
    スナップショット(Snapshot)のテーブル定義を返却します。
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
    return sqlalchemy.Table('snapshot', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('parent_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey("snapshot.id"),
                                              ),
                            sqlalchemy.Column('machine_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('machine.id'),
                                              ),
                            sqlalchemy.Column('notebook_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('notebook.id'),
                                             ),
                            sqlalchemy.Column('created_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('modified_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('name', sqlalchemy.String(256),
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_deleted', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('created', sqlalchemy.DateTime,
                                              default=now,
                                              ),
                            sqlalchemy.Column('modified', sqlalchemy.DateTime,
                                              default=now,
                                              onupdate=now,
                                              ),
                            )

class Snapshot(karesansui.db.model.Model):
    """<comment-ja>
    snapshotテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, machine, name, created_user,  modified_user,
                 notebook, parent=None, is_deleted=False):
        """<comment-ja>
        @param machine: マシン
        @type machine: Machine
        @param name: スナップショット名
        @type name: str
        @param created_user: 作成者
        @type created_user: User
        @param modified_user: 最終更新者 
        @type modified_user: User
        @param notebook: ノートブック
        @type notebook: Notebook
        @param parent: 親スナップショット
        @type parent: Snapshot
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.machine = machine
        self.name = name
        self.created_user = created_user
        self.modified_user = modified_user
        self.notebook = notebook
        self.parent = parent
        self.is_deleted = is_deleted

    def get_json(self, languages):
        ret = {}
        ret["id"] = self.id
        ret["parent_id"] = self.parent_id
        ret["created"] = self.created.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        
        ret["created_user_id"] = self.created_user_id
        ret["machine_id"] = self.machine_id
        ret["modified"] = self.modified.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        
        ret["modified_user_id"] = self.modified_user_id
        ret["is_deleted"] = self.is_deleted
        ret["name"] = self.name
        ret["notebook_id"] = self.notebook_id
        
        ret["machine"] = self.machine.get_json(languages)
        ret["modified_user"] = self.modified_user.get_json(languages)
        ret["created_user"] = self.created_user.get_json(languages)
        ret["notebook"] = self.notebook.get_json(languages)

        #if self.parent:
        #    ret["parent"] = self.parent.get_json()
        #else:
        #    ret["parent"] = None

        ret["children"] = []
        if self.children:
            for x in self.children:
                ret["children"].append(x.get_json(languages))

        return ret
    
    def __repr__(self):
        return "Snapshot<'%s'>" % (self.name)

def reload_mapper(metadata, now):
    """<comment-ja>
    Snapshot(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_snapshot = get_snapshot_table(metadata, now)
    t_machine = metadata.tables['machine']
    t_user = metadata.tables['user']

    mapper(Snapshot, t_snapshot, properties={
        'children' : relation(Snapshot,
                              backref=backref('parent',
                                              remote_side=[t_snapshot.c.id])),
                                   
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_snapshot.c.created_user_id==t_user.c.id),
        
        'modified_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_snapshot.c.modified_user_id==t_user.c.id),
        
        'machine' : relation(karesansui.db.model.machine.Machine,
                             primaryjoin=t_snapshot.c.machine_id==t_machine.c.id,
                             ),
        'notebook' : relation(karesansui.db.model.notebook.Notebook),
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
    metadata = sqlalchemy.MetaData(bind=engine)    # relation
    karesansui.db.model.machine.reload_mapper(metadata)
    karesansui.db.model.notebook.reload_mapper(metadata)
    karesansui.db.model.user.reload_mapper(metadata)
    karesansui.db.model.tag.reload_mapper(metadata)
    reload_mapper(metadata)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()    # INSERT
    # SELECT One
    # UPDATE
    # DELETE
