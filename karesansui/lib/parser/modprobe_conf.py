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
from karesansui.lib.parser.base.generic_conf_parser import genericConfParser as Parser
from karesansui.lib.utils import preprint_r
from karesansui.lib.const import VENDOR_SYSCONF_DIR, KARESANSUI_GROUP


"""
Define Variables for This Parser
"""
PARSER_MODPROBE_CONF = "/etc/modprobe.conf"

class modprobe_confParser:

    _module = "modprobe_conf"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim(" ")
        self.parser.set_new_delim(" ")
        self.parser.set_comment("#")
        self.base_parser_name = self.parser.__class__.__name__

        pass

    def source_file(self):
        retval = [PARSER_MODPROBE_CONF]

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        self.parser.set_source_file([PARSER_MODPROBE_CONF])
        conf_arr = self.parser.read_conf()
        try:
            self.dop.addconf(self._module,conf_arr[PARSER_MODPROBE_CONF]['value'])
        except:
            pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        try:
            self.dop.addconf("parser",{})
            self.dop.set("parser",[PARSER_MODPROBE_CONF],conf_arr)
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

alias eth0 e1000
alias eth1 e1000
alias eth2 e1000
alias scsi_hostadapter mptbase
alias scsi_hostadapter1 mptspi
alias scsi_hostadapter2 ata_piix
alias snd-card-0 snd-hda-intel
options snd-card-0 index=0
options snd-hda-intel index=0
remove snd-hda-intel { /usr/sbin/alsactl store 0 >/dev/null 2>&1 || : ; }; /sbin/modprobe -r --ignore-remove snd-hda-intel
include /path/to/include/file1
include /path/to/include/file2
blacklist modulename
    """

    parser = modprobe_confParser()

    # 読み込み
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())

    #########################################
    # include と blacklist パラメータの場合

    # １、パラメータを追加する
    new_key   = '/path/to/include/file1'
    new_value = ''   # valueを空にセットする
    dop.add("dum",["include",new_key],new_value)
    # コメントにするなら
    dop.comment("dum",["include",new_key])

    new_key   = '/path/to/include/file2'
    new_value = ''   # valueを空にセットする
    dop.add("dum",["include",new_key],new_value)

    # ２、パラメータを削除する
    delete_key = '/path/to/include/file2'
    dop.delete("dum",["include",delete_key])

    """
    # こっちの方式は、_multi_paramをTrueにしたときだけ

    # １、パラメータを追加する
    new_value = '/path/to/include/file'
    if dop.isset("dum",["include"]):
        old_values = dop.get("dum",["include"])
        if not new_value in old_values:
            new_values = old_values + [new_value]
    else:
        new_values = [new_value]
    dop.set("dum",["include"],new_values)

    # ２、パラメータを削除する
    new_values = []
    delete_value = '/path/to/include/file'
    if dop.isset("dum",["include"]):
        old_values = dop.get("dum",["include"])
        if delete_value in old_values:
            for _value in old_values:
                if _value != delete_value:
                    new_values.append(_value)
    else:
        pass
    if len(new_values) > 0:
        dop.set("dum",["include"],new_values)
    """

    #########################################
    # include と blacklist パラメータ以外(aliasなど)の場合

    # １、パラメータを追加する
    new_key   = 'eth3'
    new_value = 'foobar'
    dop.add("dum",["alias",new_key],new_value)
    # コメントにするなら
    dop.comment("dum",["alias",new_key])

    new_key   = "snd-hda-intel"
    new_value = "{ /usr/sbin/alsactl store 0 >/dev/null 2>&1 || : ; }; /sbin/modprobe -r --ignore-remove snd-hda-intel"
    dop.add("dum",["remove",new_key],new_value)

    # ２、パラメータを削除する
    delete_key = 'eth3'
    dop.delete("dum",["alias",delete_key])

    # ３、パラメータの値を変更する
    target_key = 'eth3'
    new_value  = 'barfoo'
    dop.set("dum",["alias",target_key],new_value)


    # 配列確認
    conf = dop.getconf("dum")
    #preprint_r(conf)

    parser.write_conf(conf,dryrun=True)

