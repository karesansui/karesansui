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
