#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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
import os.path
import sys
import re
import time
import signal
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale
    from karesansui.lib.utils import preprint_r
    from karesansui.lib.dict_op import DictOp
    from karesansui.lib.file.configfile import ConfigFile
    from karesansui.lib.utils import python_dict_to_php_array

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-m', '--module', dest='module', help=_('Module name'))
    optp.add_option('-o', '--output-file',  dest='file',  help=_('Output file name'))
    optp.add_option('-R', '--raw',  dest='raw', action="store_true", default=False, help=_('Print by raw format'))
    optp.add_option('-P', '--php',  dest='php', action="store_true", default=False, help=_('Print by php format'))
    optp.add_option('-q', '--quiet',dest='verbose', action="store_false", default=True, help=_("don't print status messages"))
    optp.add_option('-H', '--host', dest='host', help=_('Host name'))
    optp.add_option('-U', '--auth-user',  dest='auth_user',  help=_('Auth user name'))
    optp.add_option('-W', '--auth-password-file',  dest='auth_password_file',  help=_('Read auth password from file'))
    optp.add_option('-I', '--include', dest='include', help=_('Include key'), default=None)

    return optp.parse_args()

def chkopts(opts):
    if not opts.module:
        raise KssCommandOptException("ERROR: -m or --module option is required.")

    modules = opts.module.split(":")
    for _mod in modules:
        try:
            exec("from karesansui.lib.parser.%s import %sParser" % (_mod,_mod,))
        except:
            raise KssCommandOptException("ERROR: module not found. - %s" % opts.module)

    if not opts.file:
        opts.file = "/dev/stdout"
        for _cnt in range(1,len(modules)):
            opts.file = "%s:/dev/stdout" % opts.file

    files = opts.file.split(":")

    if len(modules) != len(files):
        raise KssCommandOptException("ERROR: not same number of modules and files. - module:%d file:%d" % (len(modules),len(files),))

    if opts.raw is True and opts.php is True:
        raise KssCommandOptException("ERROR: cannot specify --raw and --php option at same time.")


class ReadConf(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(1)

        dop = DictOp()
        modules = opts.module.split(":")
        files   = opts.file.split(":")

        retval = True
        cnt = 0
        for _mod in modules:
            _file = files[cnt]
            try:
                exec("from karesansui.lib.parser.%s import %sParser as Parser" % (_mod,_mod,))

                self.up_progress(5)
                parser = Parser()

                self.up_progress(5)
                if opts.raw is True:
                    raw_str = "Config_Raw_%s = {}\n" % (_mod,)
                    for _src in parser.source_file():
                        raw_str = "%sConfig_Raw_%s['%s'] = \"\"\"%s\"\"\"\n" % (raw_str,_mod,_src,open(_src).read())
                    ConfigFile(_file).write(raw_str)

                else:
                    # 設定ファイルの読み込み
                    extra_args = {}
                    extra_args["include"] = opts.include
                    conf_arr = parser.read_conf(extra_args=extra_args)
                    dop.addconf(_mod,conf_arr)
                    #dop.preprint_r(_mod)

                    # 辞書配列ファイルに書き込み
                    _var = "Config_Dict_%s" % (_mod,)
                    if opts.php is True:
                        _str = python_dict_to_php_array(dop.getconf(_mod),_var)
                        ConfigFile(_file).write(_str)
                    else:
                        ConfigFile(_file).write("%s = %s\n" % (_var,str(dop.getconf(_mod)),))

            finally:
                cnt = cnt + 1

        self.up_progress(10)
        return True

if __name__ == "__main__":
    target = ReadConf()
    sys.exit(target.run())
