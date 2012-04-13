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

from karesansui.lib.dict_op import DictOp
from karesansui.lib.parser.base.comment_deal_parser import commentDealParser as Parser
from karesansui.lib.utils import preprint_r
from karesansui.lib.const import ISCSI_DEFAULT_CONFIG_PATH

"""
Define Variables for This Parser
"""

class iscsidParser:

    _module = "hosts"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim("[ \t]*=[ \t]*")
        self.parser.set_new_delim(" = ")
        self.parser.set_comment("#")
        self.base_parser_name = self.parser.__class__.__name__
        pass

    def set_footer(self, footer=""):
        self.parser.set_footer(footer)

    def source_file(self):
        retval = [ISCSI_DEFAULT_CONFIG_PATH]

        return retval

    def read_conf(self, conf_path=None, extra_args=None):
        retval = {}

        if conf_path is None:
            conf_path = ISCSI_DEFAULT_CONFIG_PATH

        self.parser.set_source_file([conf_path])
        conf_arr = self.parser.read_conf()
        try:
            self.dop.addconf(self._module,conf_arr[conf_path]['value'])
        except:
            pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self, conf_arr={}, conf_path=None, extra_args=None, dryrun=False):
        retval = True

        if conf_path is None:
            conf_path = ISCSI_DEFAULT_CONFIG_PATH

        try:
            self.dop.addconf("parser",{})
            self.dop.set("parser",[conf_path],conf_arr)
            #self.dop.preprint_r("parser")
            arr = self.dop.getconf("parser")
            self.parser.write_conf(arr,dryrun=dryrun)
        except:
            pass

        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """
    parser = iscsidParser()
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())
    dop.add("dum",['key'],['value',[['','comment mae1','comment mae2'],'comment ato']])
    dop.comment("dum",['node.session.iscsi.FastAbort'])
    dop.uncomment("dum",['node.session.iscsi.FastAbort'])
    conf = dop.getconf("dum")
    #preprint_r(conf)
    parser.write_conf(conf,dryrun=True)
