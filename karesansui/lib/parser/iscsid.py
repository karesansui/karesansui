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
