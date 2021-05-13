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
from karesansui.lib.const import DEFAULT_LANGS

def get_watch_table(metadata, now):
    """<comment-ja>
    監視(watch)のテーブル定義を返却します。
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
    return sqlalchemy.Table('watch', metadata,
                            sqlalchemy.Column('id', sqlalchemy.Integer,
                                              primary_key=True,
                                              autoincrement=True,
                                              ),
                            sqlalchemy.Column('machine_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('machine.id'),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('created_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('modified_user_id', sqlalchemy.Integer,
                                              sqlalchemy.ForeignKey('user.id'),
                                              ),
                            sqlalchemy.Column('name', sqlalchemy.String(256),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('plugin', sqlalchemy.String(256),
                                              nullable=False,
                                              ),                                              
                            sqlalchemy.Column('plugin_selector', sqlalchemy.Text,
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('continuation_count', sqlalchemy.Integer,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('prohibition_period', sqlalchemy.Integer,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('warning_value', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_warning_percentage', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('is_warning_script', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('warning_script', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_warning_mail', sqlalchemy.Boolean,
                                              default=True,
                                              ),
                            sqlalchemy.Column('warning_mail_body', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('failure_value', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_failure_percentage', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('is_failure_script', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('failure_script', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_failure_mail', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('failure_mail_body', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_okay_script', sqlalchemy.Boolean,
                                              default=True,
                                              ),
                            sqlalchemy.Column('okay_script', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('is_okay_mail', sqlalchemy.Boolean,
                                              default=False,
                                              ),
                            sqlalchemy.Column('okay_mail_body', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('notify_mail_to', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('notify_mail_from', sqlalchemy.Text,
                                              nullable=True,
                                              ),
                            sqlalchemy.Column('karesansui_version', sqlalchemy.String(12),
                                              nullable=False,
                                              ),
                            sqlalchemy.Column('collectd_version', sqlalchemy.String(12),
                                              nullable=False,
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

class Watch(karesansui.db.model.Model):
    """<comment-ja>
    watchテーブルモデルクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, created_user, modified_user,
                 name,
                 plugin,
                 plugin_selector,
                 karesansui_version,
                 collectd_version,
                 machine,
                 continuation_count=None,
                 prohibition_period=None,
                 warning_value=None,
                 is_warning_percentage=False,
                 is_warning_script=False,
                 warning_script=None,
                 is_warning_mail=True,
                 warning_mail_body=None,
                 failure_value=None,
                 is_failure_percentage=False,
                 is_failure_script=False,
                 failure_script=None,
                 is_failure_mail=False,
                 failure_mail_body=None,
                 is_okay_script=False,
                 okay_script=None,
                 is_okay_mail=False,
                 okay_mail_body=None,
                 notify_mail_to=None,
                 notify_mail_from=None,
                 is_deleted=False,
                 ):
        """<comment-ja>
        @param created_user: 作成者
        @type  created_user: User
        @param modified_user: 最終更新者
        @type  modified_user: User
        @param name: 名前
        @type  name: str
        @param plugin: プラグイン名
        @type  plugin: str
        @param plugin_selector: プラグインセレクタ
        @type  plugin_selector: str(Text)
        @param karesansui_version: 作成したKaresansuiのバージョン
        @type  karesansui_version: str
        @param collectd_version: 作成したcollectdのバージョン
        @type  collectd_version: str
        @param machine: 監視実行マシン
        @type  machine: machine ID
        @param continuation_count: 異常検出の許容回数
        @type  continuation_count: int
        @param prohibition_period: 再アクション禁止時間
        @type  prohibition_period: int
        @param warning_value: Warningになる閾値
        @type  warning_value: str(Text)
        @param is_warning_percentage: warning_valueを%として使うか
        @type  is_warning_percentage: bool
        @param is_warning_script: Warningでスクリプトを実行するか
        @type  is_warning_script: bool
        @param warning_script: Warningで実行するスクリプト
        @type  warning_script: str(Text)
        @param is_warning_mail: Warningでメールを送信するか
        @type  is_warning_mail: bool
        @param warning_mail_body: Warningで送信するメール本体
        @type  warning_mail_body:
        @param failure_value: Failureになる閾値
        @type  failure_value: str(Text)
        @param is_failure_percentage: failure_valueを%として使うか
        @type  is_failure_percentage: bool
        @param is_failure_script: Failureでスクリプトを実行するか
        @type  is_failure_script: bool
        @param failure_script: Failureで実行するスクリプト
        @type  failure_script: str(Text)
        @param is_failure_mail: Failureでメールを送信するか
        @type  is_failure_mail: bool
        @param failure_mail_body: Failureで送信するメール本体
        @type  failure_mail_body:
        @param is_okay_script: Okayでスクリプトを実行するか
        @type  is_okay_script: bool
        @param okay_script: Okayで実行するスクリプト
        @type  okay_script: str(Text)
        @param is_okay_mail: Okayでメールを送信するか
        @type  is_okay_mail: bool
        @param okay_mail_body: Okayで送信するメール本体
        @type  okay_mail_body:
        @param notify_mail_from: 通知メールのFrom
        @type  notify_mail_from: str(Text)
        @param notify_mail_to: 通知メールのTo
        @type  notify_mail_to: str(Text)
        @param is_deleted: 削除フラグ
        @type  is_deleted: bool
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.created_user = created_user
        self.modified_user = modified_user
        self.name = name
        self.plugin = plugin
        self.plugin_selector = plugin_selector
        self.karesansui_version = karesansui_version
        self.collectd_version = collectd_version
        self.machine = machine
        self.continuation_count = continuation_count
        self.prohibition_period = prohibition_period
        self.warning_value = warning_value
        self.is_warning_percentage = is_warning_percentage
        self.is_warning_script = is_warning_script
        self.warning_script = warning_script
        self.is_warning_mail = is_warning_mail
        self.warning_mail_body = warning_mail_body
        self.failure_value = failure_value
        self.is_failure_percentage = is_failure_percentage
        self.is_failure_script = is_failure_script
        self.failure_script = failure_script
        self.is_failure_mail = is_failure_mail
        self.failure_mail_body = failure_mail_body
        self.is_okay_script = is_okay_script
        self.okay_script = okay_script
        self.is_okay_mail = is_okay_mail
        self.okay_mail_body = okay_mail_body
        self.notify_mail_to = notify_mail_to
        self.notify_mail_from = notify_mail_from
        self.is_deleted = is_deleted

    def get_json(self, languages):
        import web
        ret = {}
        ret["id"] = self.id
        ret["machine"] = self.machine.get_json(languages)

        ret["name"] = self.name
        ret["plugin"] = self.plugin
        ret["plugin_selector"] = self.plugin_selector
        ret["karesansui_version"] = self.karesansui_version
        ret["collectd_version"] = self.collectd_version
        ret["machine"] = self.machine.get_json(languages)
        ret["continuation_count"] = self.continuation_count
        ret["prohibition_period"] = self.prohibition_period
        ret["warning_value"] = self.warning_value
        ret["is_warning_percentage"] = self.is_warning_percentage
        ret["is_warning_script"] = self.is_warning_script
        ret["warning_script"] = self.warning_script
        ret["is_warning_mail"] = self.is_warning_mail
        ret["warning_mail_body"] = self.warning_mail_body
        ret["failure_value"] = self.failure_value
        ret["is_failure_percentage"] = self.is_failure_percentage
        ret["is_failure_script"] = self.is_failure_script
        ret["failure_script"] = self.failure_script
        ret["is_failure_mail"] = self.is_failure_mail
        ret["failure_mail_body"] = self.failure_mail_body
        ret["is_okay_script"] = self.is_okay_script
        ret["okay_script"] = self.okay_script
        ret["is_okay_mail"] = self.is_okay_mail
        ret["okay_mail_body"] = self.okay_mail_body
        ret["notify_mail_to"] = self.notify_mail_to
        ret["notify_mail_from"] = self.notify_mail_from

        ret["created_user"] = self.created_user.get_json(languages)
        ret["modified_user"] = self.modified_user.get_json(languages)
        ret["created"] = self.created.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        ret["created_user_id"] = self.created_user_id
        ret["modified"] = self.modified.strftime(
            DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        ret["modified_user_id"] = self.modified_user_id
        ret["is_deleted"] = self.is_deleted
        return ret

    def __repr__(self):
        return "Watch<'%s, %s'>" % (self.name,
                                        self.plugin,
                                        )
        
def reload_mapper(metadata, now):
    """<comment-ja>
    Watch(Model)のマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    @param now: now
    @type now: Datatime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    t_watch = get_watch_table(metadata, now)
    t_user = metadata.tables['user']
    t_machine = metadata.tables['machine']
    
    mapper(Watch, t_watch, properties={
        'created_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_watch.c.created_user_id==t_user.c.id),
        'modified_user' : relation(karesansui.db.model.user.User,
                                  primaryjoin=t_watch.c.modified_user_id==t_user.c.id),
        'machine' : relation(karesansui.db.model.machine.Machine,
                             primaryjoin=t_watch.c.machine_id==t_machine.c.id),
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
    karesansui.db.model.user.reload_mapper(metadata)

    reload_mapper(metadata)
    import pdb; pdb.set_trace()
    metadata.drop_all()
    metadata.create_all()
    Session = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()
    print("")
    # INSERT
    # SELECT One
    # UPDATE
    # DELETE

