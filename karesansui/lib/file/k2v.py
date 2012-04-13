#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2012 HDE, Inc.
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
