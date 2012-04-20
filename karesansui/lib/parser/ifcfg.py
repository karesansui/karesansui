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
import glob

from karesansui.lib.dict_op import DictOp
from karesansui.lib.parser.base.sh_conf_parser import shConfParser as Parser
from karesansui.lib.utils import preprint_r


"""
Define Variables for This Parser
"""
PARSER_IFCFG_DIR="/etc/sysconfig/network-scripts"
PARSER_IFCFG_FILE_PREFIX="ifcfg-"

class ifcfgParser:

    _module = "ifcfg"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.exclude_device_regex = "\.old|\.bak|\.rpm.*|lo|\.20"
        self.exclude_device_regex = "\.old|\.bak|\.rpm.*|\.20"
        self.base_parser_name = self.parser.__class__.__name__
        pass

    def source_file(self):
        retval = []

        glob_str = "%s/%s" % (PARSER_IFCFG_DIR,PARSER_IFCFG_FILE_PREFIX,)
        for _afile in glob.glob("%s*" % glob_str):
            device_name =  _afile.replace(glob_str,"")
            if re.search(r"%s" % self.exclude_device_regex, device_name) is None:
                retval.append(_afile)

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        for _afile in self.source_file():

            device_name = os.path.basename(_afile).replace(PARSER_IFCFG_FILE_PREFIX,"")
            self.parser.set_source_file([_afile])
            conf_arr = self.parser.read_conf()
            try:
                self.dop.set(self._module,[device_name],conf_arr[_afile]['value'])
            except:
                pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        for device_name,_v in conf_arr.iteritems():

            _afile = "%s/%s%s" % (PARSER_IFCFG_DIR,PARSER_IFCFG_FILE_PREFIX,device_name)
            try:
                _v['action']
                if _v['action'] == "delete":
                    if os.path.exists(_afile):
                        os.unlink(_afile)
                        #pass
            except:
                continue

            try:
                _v['value']

                self.dop.addconf("parser",{})
                self.dop.set("parser",[_afile],_v['value'])
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
    pass
