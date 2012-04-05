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

import re

from securefile import SecureFile

__all__ = ['K2V']

class K2V(SecureFile):
    """<comment-ja>
    key=value形式のファイルのread/writeを行うクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    def do_read(self, f):
        """<comment-ja>設定ファイルの読み込みを行います。
        @return: dict
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        for line in f.readlines():
            #line = re.sub(r'[ \t]', '', line).strip()
            line = line.strip()
            if len(line) <= 0 or line[0] == "#":
                continue
            key, value = line.split('=',1)
            if not value.rfind('#') == -1:
                value = value[:value.rfind('#')]
            self._data[key] = value.strip()
            
        return self._data

    def do_write(self, f, data):
        """<comment-ja>データを、読み込んだデータとマージ(上書き)します。
        書き込んだデータを再読みし、データを返却します。
        @param data: マージデータ
        @param data: dict
        @return: dict
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        for val in data.iteritems():
            self._data[val[0]] = val[1]
        for line in self._data.iteritems():
            f.write("%s=%s\n" % (line[0], line[1]))
            
        return self.read()
