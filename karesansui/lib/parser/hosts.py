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

import os
import re
import sys

from karesansui.lib.dict_op import DictOp
from karesansui.lib.parser.base.comment_deal_parser import commentDealParser as Parser
from karesansui.lib.utils import preprint_r


"""
Define Variables for This Parser
"""
PARSER_HOSTS_CONF="/etc/hosts"

class hostsParser:

    _module = "hosts"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim("[ \t]+")
        self.parser.set_new_delim("\t")
        self.parser.set_comment("#")
        self.base_parser_name = self.parser.__class__.__name__
        pass

    def source_file(self):
        retval = [PARSER_HOSTS_CONF]

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        self.parser.set_source_file([PARSER_HOSTS_CONF])
        conf_arr = self.parser.read_conf()
        try:
            self.dop.addconf(self._module,conf_arr[PARSER_HOSTS_CONF]['value'])
        except:
            pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        try:
            self.dop.addconf("parser",{})
            self.dop.set("parser",[PARSER_HOSTS_CONF],conf_arr)
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
    parser = hostsParser()
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())
    dop.add("dum",['key'],['value',[['comment foo','comment bar'],'comment hoge']])
    print dop.cdp_get("dum",['key'])
    print dop.cdp_get_pre_comment("dum",['key'])
    print dop.cdp_get_post_comment("dum",['key'])
    print dop.cdp_set("dum",['key'],"value2")
    print dop.cdp_set_pre_comment("dum",['key'],["comment foo2","comment bar2","a"])
    print dop.cdp_set_post_comment("dum",['key'],"comment fuga")
    conf = dop.getconf("dum")
    preprint_r(conf)
    parser.write_conf(conf,dryrun=True)
