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

from karesansui import KaresansuiDBException
from karesansui.lib.const import DEFAULT_LANGS

class Model(object):
    """<comment-ja>
    全てのModelの基底クラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def utf8(self, column):
        if hasattr(self, column):
            ret = getattr(self, column)
            if isinstance(ret, unicode):
                return ret.encode('utf-8')
            elif isinstance(ret, str):
                return ret
            else:
                return str(ret)
        else:
            raise 'column not found.'

    def created_locale(self, languages):
        if self.created:
            return self.created.strftime(DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        else:
            raise KaresansuiDBException("Column created is not set.")

    def modified_locale(self, languages):
        if self.modified:
            return self.modified.strftime(DEFAULT_LANGS[languages]['DATE_FORMAT'][1])
        else:
            raise KaresansuiDBException("Column modified is not set.")


def reload_mappers(metadata):
    """<comment-ja>
    全てのModelのマッパーをリロードします。
    @param metadata: リロードしたいMetaData
    @type metadata: sqlalchemy.schema.MetaData
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if metadata.bind.name == 'sqlite':
        _now = sqlalchemy.func.datetime('now', 'localtime')
    else:
        _now = sqlalchemy.func.now()

    import karesansui.db.model.user
    karesansui.db.model.user.reload_mapper(metadata, _now)

    import karesansui.db.model.tag
    karesansui.db.model.tag.reload_mapper(metadata, _now)

    import karesansui.db.model.notebook
    karesansui.db.model.notebook.reload_mapper(metadata, _now)

    import karesansui.db.model.machine2tag
    karesansui.db.model.machine2tag.reload_mapper(metadata, _now)

    import karesansui.db.model.machine
    karesansui.db.model.machine.reload_mapper(metadata, _now)

    import karesansui.db.model.snapshot
    karesansui.db.model.snapshot.reload_mapper(metadata, _now)

    import karesansui.db.model.machine2jobgroup
    karesansui.db.model.machine2jobgroup.reload_mapper(metadata, _now)

    import karesansui.db.model.watch
    karesansui.db.model.watch.reload_mapper(metadata, _now)

    import karesansui.db.model.option
    karesansui.db.model.option.reload_mapper(metadata, _now)

if __name__ == '__main__':
    pass
