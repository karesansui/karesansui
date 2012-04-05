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

import os
import re
import sys

from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.dict_op import DictOp

class nullParser:

    _comment     = ""

    _module      = "null_parser"

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
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},dryrun=False):
        retval = True
        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """
    pass
