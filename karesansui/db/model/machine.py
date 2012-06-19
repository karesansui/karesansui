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
import karesansui.db.model.user
import karesansui.db.model.tag
import karesansui.db.model.machine2tag
from karesansui.lib.const import ICON_DIR_TPL, DEFAULT_LANGS


def get_machine_table(metadata, now):
    """<comment-ja>
    マシン(Machine)のテーブル定義を返却します。
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
    return sqlalchemy.Table('machine', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('parent_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('machine.id'),
                                              nullable=True,
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
                            sqlalchemy.Column('uniq_key', sqlalchemy.Unicode(36),
                                              nullable=False,
                                              unique=True,
                                              ),
                            sqlalchemy.Column('name', sqlalchemy.String(256),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('attribute', sqlalchemy.SmallInteger,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('hypervisor', sqlalchemy.SmallInteger,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('hostname', sqlalchemy.String(256),
                                              nullable=True,
                                              unique=True,
                                              ),
                            sqlalchemy.Column('icon', sqlalchemy.String(256),
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

class Machine(karesansui.db.model.Model):
    """<comment-ja>
    machineテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    #def __init__(self):
        #pass
    
    def __init__(self, created_user, modified_user, \
                 uniq_key, name, attribute, hypervisor,
                 notebook, tags=[], hostname=None, icon=None, \
                 is_deleted=False, parent=None):
        """<comment-ja>
        @param created_user: 作成者
        @type created_user: User
        @param modified_user: 最終更新者
        @type modified_user: User
        @param uniq_key: ユニークキー
        @type uniq_key: str example) u'00000000-1111-2222-3333-444444444444'
        @param name: マシン名
        @type name: str
        @param attribute: 属性(ホスト or ゲスト...)
        @type attribute: ATTRIBUTE
        @param hypervisor: ハイパーバイザ
        @type hypervisor: HYPERVISOR
        @param notebook: ノートブック
        @type notebook: Notebook
        @param tag: タグリスト
        @type tag: [Tag...]
        @param hostname: ホスト名
        @type hostname: str
        @param icon: ファイル名
        @type icon: String
        @param is_deleted: 削除フラグ
        @type is_deleted: bool 
        @param parent: 親マシン
        @type parent: Machine
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.created_user = created_user
        self.modified_user = modified_user
        self.uniq_key = uniq_key
        self.name = name
        self.attribute = attribute
        self.hypervisor = hypervisor
        self.notebook = notebook
        self.tags = tags
        self.hostname = hostname
        self.icon = icon
        self.is_deleted = is_deleted
        self.parent = parent


    def webicon(self):
        if self.icon is None:
            return None
        else:
            import web
            return ICON_DIR_TPL % (web.ctx.homepath, self.icon)
    
    def realicon(self):
        if self.icon is None:
            return None
        else:
            return ICON_DIR_TPL % (karesansui.dirname, self.icon)

    def get_json(self, languages):
        import web
        ret = {}
        ret["id"] = self.id
        #ret["icon"] = "%s/data/icon/machine/%d"  % (web.ctx.homepath, self.id)
        ret["icon"] = self.webicon()
        ret["attribute"] = self.attribute
        ret["hostname"] = self.hostname
        try:
            ret["created"] = self.created.strftime(
                DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        except:
            ret["created"] = ""

        ret["created_user_id"] = self.created_user_id
        ret["is_deleted"] = self.is_deleted
        try:
            ret["modified"] = self.modified.strftime(
                DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        except:
            ret["modified"] = ""

        ret["modified_user_id"] = self.modified_user_id
        ret["name"] = self.name
        ret["notebook_id"] = self.notebook_id
        ret["parent_id"] = self.parent_id
        ret["uniq_key"] = self.uniq_key
        ret["hypervisor"] = self.hypervisor

        try:
            ret["created_user"] = self.created_user.get_json(languages)
            ret["modified_user"] = self.modified_user.get_json(languages)
            ret["notebook"] = self.notebook.get_json(languages)
        except:
            ret["created_user"] = ""
            ret["modified_user"] = ""
            ret["notebook"] = ""
        
        #if  self.parent:
        #    ret["parent"] = self.parent.get_json()
        #else:
        #    ret["parent"] = None
        
        ret["children"] = []
        if self.children:
            for x in self.children:
                if not x.is_deleted:
                    ret["children"].append(x.get_json(languages))
        
        ret["tags"] = []
        if self.tags:
            for x in self.tags:
                ret["tags"].append(x.get_json(languages))
            
        return ret

    def __repr__(self):
        return "Machine<'%s, %s, %s'>" % (self.uniq_key,
                                   self.name,
                                   self.is_deleted)
        
def reload_mapper(metadata, now):
    """<comment-ja>
    Machine(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_machine = get_machine_table(metadata, now)
    t_machine_tag = metadata.tables['machine2tag']
    t_user = metadata.tables['user']
    
    mapper(Machine, t_machine, properties={
        'children' : relation(Machine,
                              backref=backref('parent',
                                              remote_side=[t_machine.c.id])),
        'notebook' : relation(karesansui.db.model.notebook.Notebook),
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_machine.c.created_user_id==t_user.c.id),
        'modified_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_machine.c.modified_user_id==t_user.c.id),
        'tags' : relation(karesansui.db.model.tag.Tag,
                         secondary=t_machine_tag,
                         backref="machine"),
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
    karesansui.db.model.notebook.reload_mapper(metadata)
    karesansui.db.model.user.reload_mapper(metadata)
    karesansui.db.model.tag.reload_mapper(metadata)

    reload_mapper(metadata)
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()
    print ""
    # INSERT
    # SELECT One
    # UPDATE
    # DELETE

