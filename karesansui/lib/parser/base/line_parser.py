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

import os
import re
import sys

from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.dict_op import DictOp
from karesansui.lib.utils import execute_command

class lineParser:

    _comment     = ""

    _module      = "line_parser"

    def __init__(self,paths=[]):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})
        self.set_source_file(paths)

    def set_comment(self, comment=""):
        self._comment = comment

    def set_source_file(self,paths=[]):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths
        return True

    def get_source_file(self):
        return self.paths

    def source_file(self):
        return self.get_source_file()

    def read_conf(self):
        retval = {}

        for _afile in self.source_file():
            if _afile[0:4] == "cmd:":
                command_args = _afile[4:].split()
                (ret,res) = execute_command(command_args)
            else:
                res = ConfigFile(_afile).read()

            new_res = []
            for _aline in res:
                _aline = _aline.rstrip('\r\n')
                if self._comment != "" and not _aline.rfind(self._comment) == -1:
                    _aline = _aline[:_aline.rfind(self._comment)]
                if _aline != "":
                    new_res.append(_aline)
            self.dop.set(self._module,[_afile],new_res)

        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},dryrun=False):
        retval = True

        for _path,_v in conf_arr.iteritems():

            if _path[0:1] != "/":
                continue

            try:
                _v['value']
            except:
                continue

            if dryrun is False:
                ConfigFile(_path).write("\n".join(_v['value']) + "\n")
            else:
                print "\n".join(_v['value'])

        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """
    filename = "/etc/hosts"
    parser = lineParser(filename)
    #parser.set_comment("#")
    conf = parser.read_conf()
    parser.write_conf(conf,dryrun=True)
