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

import fcntl
import sys

__all__ = ["SecureFile"]

class SecureFile:
    
    _path = None
    _data = {}

    def __init__(self, path):
        """<comment-ja>pathを元に設定ファイルを読み込む
        @param path: 設定ファイルのパス
        @type path: str
        @param autoread: 自動で読み込みを行うかどうか
        @type autoread: bool 
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self._path = path

    def __lock_SH(self, f):
        """<comment-ja>
        共有ロックを取得(読み込みの時に使用)
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        fcntl.lockf(f.fileno(), fcntl.LOCK_SH)
        
    def __lock_EX(self, f):
        """<comment-ja>
        排他的ロックを取得(書き込みの時に使用)
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        fcntl.lockf(f.fileno(), fcntl.LOCK_EX)
        
    def __lock_UN(self, f):
        """<comment-ja>
        アンロック(読み込み/書き込みの時に使用) 
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        fcntl.lockf(f.fileno(), fcntl.LOCK_UN)

    def do_read(self):
        raise Exception("Please override.")

    def read(self):
        try:
            f = open(self._path, 'r')
            try:
                self.__lock_SH(f)
                try:
                    return self.do_read(f)
                finally:
                    self.__lock_UN(f)
            finally:
                f.close()
        except Exception, e:
            print >>sys.stdout, '"%s" : Error reading config file. %s' % (self._path, e.args)
            raise

    def do_write(self, data):
        raise Exception("Please override.")

    def write(self, data):
        try:
            f = open(self._path, "w")
            try:
                self.__lock_EX(f)
                try:
                    return self.do_write(f, data)
                finally:
                    self.__lock_UN(f)
            finally:
                f.close()
                    
        except Exception, e:
            print >>sys.stdout, '"%s" : Error writing config file. %s' % (self._path, e.args)
            raise
        
if __name__ == '__main__':
    pass
