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
