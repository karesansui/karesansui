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
    from karesansui.lib.utils import copy_file
    from karesansui.lib.utils import execute_command
    from karesansui.lib.utils import preprint_r, base64_decode
    from karesansui.lib.utils import php_array_to_python_dict
    from karesansui.lib.dict_op import DictOp

except ImportError as e:
    print("[Error] some packages not found. - %s" % e, file=sys.stderr)
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-m', '--module', dest='module', help=_('Module name'))
    optp.add_option('-i', '--input-file',  dest='file',  help=_('Input file name'))
    optp.add_option('-q', '--quiet',dest='verbose', action="store_false", default=True, help=_("don't print status messages"))
    optp.add_option('-D', '--delete',dest='delete', action="store_true", default=False, help=_("Remove the specified dict file after execution."))
    optp.add_option('-E', '--early-exit',dest='early_exit', action="store_true", default=False, help=_("Exit, once the module's write process is failed."))
    optp.add_option('-P', '--php',  dest='php', action="store_true", default=False, help=_('If the input file format is php script, this should be specified.'))
    optp.add_option('-j', '--pre-command',  dest='pre_command',  default=None, help=_('Execute scriptlet before writing.'))
    optp.add_option('-J', '--post-command',  dest='post_command',  default=None, help=_('Execute scriptlet after writing.'))
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
        raise KssCommandOptException("ERROR: -i or --input-file option is required.")

    files = opts.file.split(":")
    for _file in files:
        if not os.path.exists(_file):
            raise KssCommandOptException("ERROR: file not found. - %s" % _file)


        if opts.php is True:
            try:
                _dict = php_array_to_python_dict(open(_file).read())
            except:
                raise
                raise KssCommandOptException("ERROR: file format is invalid. - %s" % _file)

        else:
            try:
                exec("%s" % open(_file).read())
            except:
                raise KssCommandOptException("ERROR: file format is invalid. - %s" % _file)

    if len(modules) != len(files):
        raise KssCommandOptException("ERROR: not same number of modules and files. - module:%d file:%d" % (len(modules),len(files),))


class WriteConf(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(1)

        uniq_id = time.strftime("%Y%m%d%H%M%S", time.localtime())

        if opts.pre_command is not None:
            if opts.pre_command[0:4] == "b64:":
                command = base64_decode(opts.pre_command[4:])
            else:
                command = opts.pre_command
            self.logger.info("execute command - %s" % command)
            (_ret,_res) = execute_command(command.split())
            if _ret != 0:
                error_msg = "execute error - %s" % command
                self.logger.error(error_msg)
                #raise KssCommandOptException("ERROR: %s" % error_msg)

        dop = DictOp()
        modules = opts.module.split(":")
        files   = opts.file.split(":")

        source_files = []
        retval = True
        cnt = 0
        for _mod in modules:
            _file = files[cnt]
            try:
                exec("from karesansui.lib.parser.%s import %sParser as Parser" % (_mod,_mod,))

                self.up_progress(5)
                parser = Parser()

                # 辞書オペレータに追加
                self.up_progress(5)
                if opts.php is True:
                    conf_arr = php_array_to_python_dict(open(_file).read())
                else:
                    exec("conf_arr = %s" % open(_file).read())
                dop.addconf(_mod,conf_arr)

                """
                必要ならここで配列操作
                通常は、配列操作後の辞書が_fileに書き込まれているので必要ない
                dop.add   (_mod,"foo","bar")
                dop.delete(_mod,"foo")
                """

                # 設定ファイル一覧に作成（バックアップ用）
                self.up_progress(5)
                source_file = parser.source_file()
                for _afile in source_file:
                    _bak_afile = "%s.%s" % (_afile,uniq_id)
                    copy_file(_afile,_bak_afile)
                source_files = source_files + source_file

                # 辞書に戻す
                self.up_progress(5)
                conf_arr = dop.getconf(_mod)
                #dop.preprint_r(_mod)

                # 設定ファイルに書き込み
                self.up_progress(5)
                extra_args = {}
                extra_args["include"] = opts.include
                if opts.early_exit is True:
                    retval = retval and parser.write_conf(conf_arr,extra_args=extra_args)
                else:
                    retval = parser.write_conf(conf_arr,extra_args=extra_args) and retval

                if opts.delete is True:
                    os.unlink(_file)

            finally:
                cnt = cnt + 1

        if retval is False:
            for _afile in source_files:
                _bak_afile = "%s.%s" % (_afile,uniq_id)
                os.unlink(_afile)
                copy_file(_bak_afile,_afile)
                os.unlink(_bak_afile)
            raise KssCommandOptException("ERROR: write configure failure")

        for _afile in source_files:
            _bak_afile = "%s.%s" % (_afile,uniq_id)
            os.unlink(_bak_afile)

        if opts.post_command is not None:
            if opts.post_command[0:4] == "b64:":
                command = base64_decode(opts.post_command[4:])
            else:
                command = opts.post_command
            self.logger.info("execute command - %s" % command)
            (_ret,_res) = execute_command(command.split())
            if _ret != 0:
                error_msg = "execute error - %s" % command
                self.logger.error(error_msg)
                raise KssCommandOptException("ERROR: %s" % error_msg)

        self.up_progress(10)
        return True

if __name__ == "__main__":
    target = WriteConf()
    sys.exit(target.run())
