#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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

import os
import time
import types

from bsddb import hashopen, btopen
from karesansui.lib.const import COUNTUP_DATABASE_PATH, KARESANSUI_GROUP

"""
Berkeley DBにキーの値（カウント情報）を書き込む

キー：カテゴリー名(半角文字)
値  ：以下の要素を持つリスト配列のstrでキャストした文字列
       要素0: total        同一アラート抑制スパン(span)内の合計ヒット回数
                           (since + span)の期間に何回ヒットしたか
                           reset(attr="total")で初期化
                           up()でインクリメント
       要素1: hitcount     回数監視スパン(seconds)内のカテゴリーのヒット回数
                           (start + seconds)の期間に何回ヒットしたか
                           reset(attr="hitcount")で初期化
                           up()でインクリメント
       要素2: continuation 監視間隔(interval)での連続ヒット回数
                           reset(attr="continuation")で初期化
                           mtime + interval + 1 内にヒットすればカウント
                           以外なら、1でリセット
                           up(attr="continuation")でインクリメント
       要素3: since        初期データ投入時刻(Unixtime)
                           同一アラート抑制スパン制御のための開始時刻
                           reset(attr="total")で初期化
       要素4: start        hitcountのリセット時刻(Unixtime)
                           回数監視スパン制御のための開始時刻
                           reset(attr="hitcount")で初期化
       要素5: mtime        最終更新時刻(Unixtime)
                           最終ヒット時刻
       要素6: action       sinceからのアクション回数

Example:

>>> from karesansui.lib.collectd.countup import CountUp
>>> countup = CountUp()
>>> 
>>> countup.init("memory_used_exceeded")
>>> print countup.get("memory_used_exceeded")
[0, 0, 0, 1271224396.0812089, 1271224396.0812089, 1271224396.0812089, 0]
>>> countup.up("memory_used_exceeded")
>>> print countup.get("memory_used_exceeded")
[1, 1, 0, 1271224396.0812089, 1271224396.0812089, 1271224396.0870471, 1]
>>> countup.up("memory_used_exceeded")
>>> countup.reset("memory_used_exceeded",attr="hitcount")
>>> countup.reset("memory_used_exceeded")
>>> countup.finish()

"""

class CountUp:

    path = None

    def __init__(self, path=None):
        if path is None:
            self.path = COUNTUP_DATABASE_PATH
        else:
            self.path = path

        self.attrs = ["total","hitcount","continuation","since","start","mtime","action"]

        self._set_db_type("bt")     # B-Tree
        self._set_db_type("hash")   # Hash

        try:
            self.create()
        except:
            raise

    def _set_db_type(self,type="hash"):
        self.db_type = type

    def _open(self, flag="c", mode=0000):
        func = "%sopen" % self.db_type
        try:
            exec("ret = %s(self.path, flag, mode)" % func)
            return ret
        except:
            raise

    def _close(self):
        try:
            self.db.close()
        except:
            pass

    def create(self):
        if not os.path.exists(self.path):
            self.db = self._open("c")
            from karesansui.lib.utils import r_chmod, r_chgrp
            r_chgrp(self.path,KARESANSUI_GROUP)
            r_chmod(self.path,"g+rw")
        else:
            self.db = self._open("c")
        pass

    def destroy(self):
        self._close()
        if os.path.exists(self.path):
            os.unlink(self.path)

    def finish(self):
        self._close()

    def init(self,key):
        retval = False

        now = time.time()
        value = [0,0,0,now,now,now,0]

        try:
            self.db[key] = str(value)
            retval = True
        except:
            pass

        return retval

    def get(self,key,attr=None):
        retval = []

        if self.db.has_key(key) == 1:
            exec("retval = %s" % self.db[key])

            if attr is not None:
                if attr in self.attrs:
                    retval = retval[self.attrs.index(attr)]

        return retval

    def get_total(self,key):
        return self.get(key,attr="total")

    def get_hitcount(self,key):
        return self.get(key,attr="hitcount")

    def get_continuation(self,key):
        return self.get(key,attr="continuation")

    def get_since(self,key):
        return self.get(key,attr="since")

    def get_start(self,key):
        return self.get(key,attr="start")

    def get_mtime(self,key):
        return self.get(key,attr="mtime")

    def get_action(self,key):
        return self.get(key,attr="action")

    def set(self,key,value,attr=None):
        retval = False

        if self.db.has_key(key) == 1:

            exec("data = %s" % self.get(key))

            modified = False
            if attr is None:
                if type(value) is types.ListType:
                    data = value
                    modified = True
            else:
                if attr in self.attrs:
                    data[self.attrs.index(attr)] = value
                    modified = True

            if modified is True:
                try:
                    self.db[key] = str(data)
                    retval = True
                except:
                    pass

        else:
            if type(value) is types.ListType:
                try:
                    self.db[key] = str(value)
                    retval = True
                except:
                    pass

        return retval

    def up(self,key,attr=None):
        retval = False

        now = time.time()
        if self.db.has_key(key) == 1:
            data = self.get(key)
            try:
                total = int(data[self.attrs.index("total")])
            except:
                total = 0
            try:
                hitcount = int(data[self.attrs.index("hitcount")])
            except:
                hitcount = 0
            try:
                continuation = int(data[self.attrs.index("continuation")])
            except:
                continuation = 0
            try:
                action = int(data[self.attrs.index("action")])
            except:
                action = 0

            if attr is None:
                total += 1
                hitcount += 1
            elif attr == "total":
                total += 1
            elif attr == "hitcount":
                hitcount += 1
            elif attr == "continuation":
                continuation += 1
            elif attr == "action":
                action += 1

            data[0] = total
            data[1] = hitcount
            data[2] = continuation
            data[5] = now
            data[6] = action

        else:
            data = [1,1,1,now,now,now,0]

        try:
            self.set(key,data)
            retval = True
        except:
            pass

        return retval

    def reset(self,key,attr=None,value=0):
        retval = False

        now = time.time()
        if self.db.has_key(key) == 1:
            data = self.get(key)

            if attr is None:
                data[0] = value
                data[1] = value
                data[3] = now
                data[4] = now
            elif attr == "total":
                data[0] = value
                data[3] = now
            elif attr == "hitcount":
                data[1] = value
                data[4] = now
            elif attr == "continuation":
                data[3] = value
            elif attr == "action":
                data[6] = 0

        else:
            data = [value,value,value,now,now,now,0]

        try:
            self.set(key,data)
            retval = True
        except:
            pass

        return retval


if __name__ == '__main__':

  countup = CountUp()

  countup.init("memory_used_exceeded")
  print countup.get("memory_used_exceeded")

  countup.up("memory_used_exceeded")
  print countup.get("memory_used_exceeded")

  countup.up("memory_used_exceeded")
  print countup.get_hitcount("memory_used_exceeded")
  print countup.get_mtime("memory_used_exceeded")

  countup.reset("memory_used_exceeded",attr="hitcount")
  print countup.get("memory_used_exceeded")

  countup.up("memory_used_exceeded",attr="continuation")
  print countup.get("memory_used_exceeded")

  countup.up("memory_used_exceeded")
  print countup.get("memory_used_exceeded")

  countup.reset("memory_used_exceeded")
  print countup.get("memory_used_exceeded")

  countup.finish()

