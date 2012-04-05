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
from karesansui.lib.parser.base.xml_like_conf_parser import xmlLikeConfParser as Parser
from karesansui.lib.utils import preprint_r
from karesansui.lib.const import VENDOR_SYSCONF_DIR, \
                                 COLLECTD_DATA_DIR, KARESANSUI_GROUP


"""
Define Variables for This Parser
"""
PARSER_COLLECTD_CONF = "%s/collectd.conf" % VENDOR_SYSCONF_DIR

class collectdParser:

    _module = "collectd"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim("[ \t]+")
        self.parser.set_new_delim("\t")
        self.parser.set_comment("#")
        self.base_parser_name = self.parser.__class__.__name__

        self.opt_uni   = ['Hostname',
                          'FQDNLookup',
                          'BaseDir',
                          'PIDFile',
                          'Target',
                          'Host',
                          'Key',
                          'LogLevel',
                          'Plugin',
                          'Subject',
                          'SMTPPort',
                          'SMTPServer',
                          'URL',
                          'Type',
                          'Chain']
        self.opt_multi = ['Include',
                          'LoadPlugin',
                          'Collect',
                          'DriverOption',
                          'GetCapacity',
                          'GetSnapshot',
                          'Irq',
                          'JVMArg',
                          'Listen',
                          'PreCacheChain',
                          'PostCacheChain',
                          'Query',
                          'Recipient',
                          'Sensor',
                          'Server',
                          'WatchAdd']
        self.opt_sect  = ['Plugin',
                          'LoadPlugin',
                          'Threshold',
                          'Type',
                          'Chain',
                          'Data',
                          'Database',
                          'Directory',
                          'Disks',
                          'File',
                          'Host',
                          'Key',
                          'Match',
                          'Metric',
                          'Module',
                          'Page',
                          'Query',
                          'Recursor',
                          'Result',
                          'Router',
                          'Rule',
                          'Server',
                          'System',
                          'Table',
                          'Target',
                          'URL',
                          'View',
                          'VolumePerf',
                          'VolumeUsage',
                          'WAFL']

        self.parser.set_opt_uni(self.opt_uni)
        self.parser.set_opt_multi(self.opt_multi)
        self.parser.set_opt_sect(self.opt_sect)

        pass

    def set_footer(self, footer=""):
        self.parser.set_footer(footer)

    def source_file(self):
        retval = [PARSER_COLLECTD_CONF]

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        self.parser.set_source_file([PARSER_COLLECTD_CONF])
        conf_arr = self.parser.read_conf()
        try:
            self.dop.addconf(self._module,conf_arr[PARSER_COLLECTD_CONF]['value'])
        except:
            pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        try:
            self.dop.addconf("parser",{})
            self.dop.set("parser",[PARSER_COLLECTD_CONF],conf_arr)
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
    parser = collectdParser()

    # 読み込み
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())

    ##########################################################
    # Uniオプション (一箇所しか設定できないオプション) の追加
    ##########################################################
    # 'Foo foo' を追加（設定値リスト形式モードよる addメソッド）
    dop.add("dum",["Foo"],["foo",[["comment foo1","comment foo2"],"comment foo3"]])
    #print dop.cdp_get("dum",["Foo"])
    #print dop.cdp_get_pre_comment("dum",["Foo"])
    #print dop.cdp_get_post_comment("dum",["Foo"])
    dop.insert_order("dum",["Foo"])

    # 'Bar bar' を追加（設定値文字列形式モードによる cdp_setメソッド）
    dop.cdp_set("dum",["Bar"],"bar")
    dop.cdp_set_pre_comment("dum",["Bar"],["","comment bar1","comment bar2"])
    dop.cdp_set_post_comment("dum",["Bar"],"comment bar3")
    dop.insert_order("dum",["Bar"])

    ##########################################################
    # Multiオプション (複数設定できるオプション) の追加
    ##########################################################
    # 'LoadPlugin target_hoge' を追加
    dop.cdp_set("dum",["LoadPlugin","target_hoge"],"target_hoge",is_opt_multi=True)
    dop.cdp_set_pre_comment("dum",["LoadPlugin","target_hoge"],["","Dis is target_hoge"])

    ##########################################################
    # Sectオプション (<ブラケット>ディレクティブオプション) の追加
    ##########################################################
    # 下記 を追加
    # <Plugin "foobar">
    #        <View "hoge">
    #                SubOpt1         gege # post
    #        </View>
    #        Option2         false
    #        Option1         true
    # </Plugin>
    dop.cdp_set("dum",["Plugin","foobar","Option1"],"true")
    dop.cdp_set("dum",["Plugin","foobar","Option2"],"false")
    dop.cdp_set("dum",["Plugin","foobar","View","hoge","SubOpt1"],"gege")
    dop.cdp_set_pre_comment("dum",["Plugin","foobar","View","hoge","SubOpt1"],["","pre comment"])
    dop.cdp_set_post_comment("dum",["Plugin","foobar","View","hoge","SubOpt1"],"post")

    # 'LoadPlugin target_replace' の値を取得
    key = ["LoadPlugin","target_hoge"]
    dop.insert_order("dum",key)
    value = dop.cdp_get("dum",key)
    preprint_r(value)

    # 'LoadPlugin target_replace' の設定順を取得
    key = ["LoadPlugin","target_hoge"]
    num = dop.order("dum",key)
    print num

    # '<Plugin foobar>' を 'LoadPlugin target_hoge' の前にする
    key = ["Plugin","foobar"]
    dop.insert_order("dum",key,num)

    # '<Plugin foobar>' を 'LoadPlugin target_hoge' の後に変更する
    dop.change_order("dum",key,num+1)

    # 'Foo' を 'Bar' の後に変更する
    num = dop.order("dum",['Foo'])
    dop.change_order("dum",['Bar'],num+1)
    print dop.get("dum",['@ORDERS'])

    # 配列確認
    conf = dop.getconf("dum")
    #preprint_r(conf)

    #parser.set_footer("")
    parser.write_conf(conf,dryrun=True)

