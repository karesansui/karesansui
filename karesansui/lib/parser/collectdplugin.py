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
from karesansui.lib.parser.base.xml_like_conf_parser import xmlLikeConfParser as Parser
from karesansui.lib.utils import preprint_r, r_chgrp, r_chmod
from karesansui.lib.const import VENDOR_SYSCONF_DIR, \
                                 COLLECTD_DATA_DIR, KARESANSUI_GROUP


"""
Define Variables for This Parser
"""
PARSER_COLLECTD_PLUGIN_DIR = "%s/collectd.d" % VENDOR_SYSCONF_DIR

class collectdpluginParser:

    _module = "collectdplugin"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.parser = Parser()
        self.parser.set_delim("[ \t]+")
        self.parser.set_new_delim("\t")
        self.parser.set_comment("#")
        self.base_parser_name = self.parser.__class__.__name__

        from karesansui.lib.parser.collectd import collectdParser
        collectdp = collectdParser()

        self.parser.set_opt_uni(collectdp.opt_uni)
        self.parser.set_opt_multi(collectdp.opt_multi)
        self.parser.set_opt_sect(collectdp.opt_sect)

        pass

    def set_footer(self, footer=""):
        self.parser.set_footer(footer)

    def source_file(self):
        retval = []

        glob_str = "%s/*.conf" % (PARSER_COLLECTD_PLUGIN_DIR,)
        for _afile in glob.glob(glob_str):
            retval.append(_afile)

        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        for _afile in self.source_file():

            plugin_name = re.sub("\.conf$","",os.path.basename(_afile))

            try:
                extra_args['include']
                if not re.search(extra_args['include'],plugin_name):
                    continue
            except:
                pass

            self.parser.set_source_file([_afile])
            conf_arr = self.parser.read_conf()
            try:
                self.dop.set(self._module,[plugin_name],conf_arr[_afile]['value'])
            except:
                pass

        self.dop.set(self._module,['@BASE_PARSER'],self.base_parser_name)
        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)

    def _pre_write_conf(self,conf_arr={}):

        # Change permission to be able to read/write data kss group.
        if os.path.exists(COLLECTD_DATA_DIR):
            if os.getuid() == 0:
                r_chgrp(COLLECTD_DATA_DIR,KARESANSUI_GROUP)
                r_chmod(COLLECTD_DATA_DIR,"g+rwx")
                r_chmod(COLLECTD_DATA_DIR,"o-rwx")

        dop = DictOp()
        dop.addconf("__",conf_arr)

        if dop.isset("__",["python"]) is True:
            dop.cdp_unset("__",["python","Plugin","python","@ORDERS"],multiple_file=True)
            orders = []
            orders.append(['Encoding'])
            orders.append(['LogTraces'])
            orders.append(['Interactive'])
            orders.append(['ModulePath'])
            orders.append(['Import'])
            orders.append(['Module'])
            dop.cdp_set("__",["python","Plugin","python","@ORDERS"],orders,is_opt_multi=True,multiple_file=True)

        return dop.getconf("__")

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        conf_arr = self._pre_write_conf(conf_arr)

        for plugin_name,_v in conf_arr.iteritems():

            _afile = "%s/%s.conf" % (PARSER_COLLECTD_PLUGIN_DIR,plugin_name,)
            try:
                _v['action']
                if _v['action'] == "delete":
                    if os.path.exists(_afile):
                        os.unlink(_afile)
                        continue
            except:
                pass
                #continue

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

    parser = collectdpluginParser()

    # 読み込み
    dop = DictOp()
    dop.addconf("dum",parser.read_conf())

    new_plugin_name = "takuma"

    ##########################################################
    # Uniオプション (一箇所しか設定できないオプション) の追加
    ##########################################################
    # 'Foo foo' を追加（設定値リスト形式モードよる addメソッド）
    dop.add("dum",[new_plugin_name,"Foo"],["foo",[["comment foo1","comment foo2"],"comment foo3"]])

    # 'Bar bar' を追加（設定値文字列形式モードによる cdp_setメソッド）
    dop.cdp_set("dum",[new_plugin_name,"Bar"],"bar",multiple_file=True)
    dop.cdp_set_pre_comment("dum",[new_plugin_name,"Bar"],["","comment bar1","comment bar2"],multiple_file=True)
    dop.cdp_set_post_comment("dum",[new_plugin_name,"Bar"],"comment bar3",multiple_file=True)

    ##########################################################
    # Multiオプション (複数設定できるオプション) の追加
    ##########################################################
    # 'LoadPlugin target_hoge' を追加
    dop.cdp_set("dum",[new_plugin_name,"LoadPlugin","target_hoge"],"target_hoge",multiple_file=True,is_opt_multi=True)
    dop.cdp_set_pre_comment("dum",[new_plugin_name,"LoadPlugin","target_hoge"],["","Dis is target_hoge"],multiple_file=True)

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
    dop.cdp_set("dum",[new_plugin_name,"Plugin","foobar","Option1"],"true",multiple_file=True)
    dop.cdp_set("dum",[new_plugin_name,"Plugin","foobar","Option2"],"false",multiple_file=True)
    dop.cdp_set_pre_comment("dum",[new_plugin_name,"Plugin","foobar","Option2"],"pre comment",multiple_file=True)
    dop.cdp_set_post_comment("dum",[new_plugin_name,"Plugin","foobar","Option2"],"post comment",multiple_file=True)
    dop.cdp_set("dum",[new_plugin_name,"Plugin","foobar","View","hoge","SubOpt1"],"gege",multiple_file=True)
    dop.cdp_set_post_comment("dum",[new_plugin_name,"Plugin","foobar","View","hoge","SubOpt1"],"post",multiple_file=True)

    print dop.get("dum",["filter","@ORDERS"],multiple_file=True)

    # 複数ファイルを読み込むパーサーの場合は、is_parent_parser=Trueにすること
    # '<Plugin foobar>' を 先頭にする
    key = [new_plugin_name,"Plugin","foobar"]
    dop.insert_order("dum",key,0,is_parent_parser=True)

    # 'LoadPlugin target_hoge' を 先頭にする => '<Plugin foobar>' は２番目になる
    key = [new_plugin_name,"LoadPlugin","target_hoge"]
    dop.insert_order("dum",key,0,is_parent_parser=True)

    # 'Foo foo' を 先頭にする => 'LoadPlugin target_hoge' は２番目になる
    key = [new_plugin_name,"Foo"]
    dop.insert_order("dum",key,0,is_parent_parser=True)

    # work completely
    #dop.cdp_comment("dum",["python","Plugin","python","Import"],multiple_file=True)
    #dop.cdp_comment("dum",["python","Plugin","python","Module","notification"],multiple_file=True)
    #dop.cdp_comment("dum",["python","Plugin","python","Module","notification","CountupDBPath"],multiple_file=True)
    #dop.cdp_set("dum",["python","Plugin","python","Module","notification","@ORDERS"],[['Environ'],['CountupDBPath']],multiple_file=True,is_opt_multi=True)
    # work completely, too.
    #dop.cdp_comment("dum",["python","Plugin","python","ModulePath"],multiple_file=True)
    # work completely, too. (but this is overwritten by _pre_write_conf() method)
    #dop.cdp_set("dum",["python","Plugin","python","@ORDERS"],[['ModulePath'],['Encoding']],multiple_file=True,is_opt_multi=True)
    #sys.exit()

    # 配列確認
    conf = dop.getconf("dum")
    preprint_r(conf)

    parser.write_conf(conf,dryrun=True)
