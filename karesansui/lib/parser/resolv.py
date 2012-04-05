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
from karesansui.lib.parser.base.sh_conf_parser import shConfParser as Parser
from karesansui.lib.utils import preprint_r


"""
Define Variables for This Parser
"""
PARSER_RESOLV_CONF="/etc/resolv.conf"

class resolvParser:

    _module = "resolv"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim(" ")
        self.parser.set_new_delim(" ")
        self.parser.set_multidefine(True)
        self.base_parser_name = self.parser.__class__.__name__
        pass

    def source_file(self):
        retval = [PARSER_RESOLV_CONF]

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        self.parser.set_source_file([PARSER_RESOLV_CONF])
        conf_arr = self.parser.read_conf()
        try:
            self.dop.addconf(self._module,conf_arr[PARSER_RESOLV_CONF]['value'])
        except:
            pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        try:
            self.dop.addconf("parser",{})
            self.dop.set("parser",[PARSER_RESOLV_CONF],conf_arr)
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
    parser = resolvParser()
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())
    dop.comment("dum","search")
    dop.comment("dum","nameserver")
    dop.add("dum","domain","example.com localdomain")
    conf = dop.getconf("dum")
    parser.write_conf(conf,dryrun=True)
