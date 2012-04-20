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

"""
シェルスクリプトを実行する

引数１：スクリプトの内容
引数２：実行ユーザー
引数３：メッセージ
引数４：監視項目名
引数５：ログファイル

"""

import os, sys, pwd, re, fcntl, tempfile

from karesansui.lib.const import KARESANSUI_PREFIX, KARESANSUI_DATA_DIR, \
                                 KARESANSUI_USER, KARESANSUI_GROUP
from karesansui.lib.utils import execute_command, r_chmod, r_chown, r_chgrp
from karesansui.lib.collectd.utils import append_line

def exec_script(script="",user="root",msg="",watch_name="",logfile="/dev/null"):
    retval = False

    func_name = sys._getframe(0).f_code.co_name
    append_line(logfile,"[%s] Entering function '%s'." % (func_name,func_name,))

    # スクリプトの一時保存ディレクトリを作成
    SCRIPT_TMP_DIR = "%s/tmp/.script" % (KARESANSUI_DATA_DIR,)
    if not os.path.exists(SCRIPT_TMP_DIR):
        os.makedirs(SCRIPT_TMP_DIR)
        r_chmod(SCRIPT_TMP_DIR,0770)
        r_chown(SCRIPT_TMP_DIR,KARESANSUI_USER)
        r_chgrp(SCRIPT_TMP_DIR,KARESANSUI_GROUP)
        append_line(logfile,"[%s] Create directory '%s'." % (func_name,SCRIPT_TMP_DIR,))

    try:
       user_id = int(user)
    except:
       user_id = pwd.getpwnam(user)[2]

    # スクリプトファイルの生成
    fname = None
    try:
        fd, fname  = tempfile.mkstemp(suffix="",prefix="script_",dir=SCRIPT_TMP_DIR)
        append_line(logfile,"[%s] Create script '%s'." % (func_name,fname,))
        fp = os.fdopen(fd,"w")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_EX)
        script = re.sub("%{watch_name}",watch_name.encode('utf_8'),script)
        script = re.sub("%{msg}"       ,msg.encode('utf_8')       ,script)
        fp.write(script)
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
        os.chmod(fname,0700)
        os.chown(fname,user_id,-1)

    except:
        append_line(logfile,"[%s] Error: failed to create script." % (func_name,))
        if fname is not None and os.path.exists(fname):
            os.unlink(fname)

    if fname is not None and os.path.exists(fname):

        # マジッククッキーを調べる
        magic_cookie = open(fname).readline().rstrip()
        if magic_cookie[-8:] == "bin/perl":
            interpreter = "perl"
        elif magic_cookie[-10:] == "bin/python" or \
             magic_cookie[-10:] == "env python":
            interpreter = "python"
        elif magic_cookie[-7:] == "bin/php":
            interpreter = "php"
        elif magic_cookie[-8:] == "bin/ruby":
            interpreter = "ruby"
        elif magic_cookie[-8:] == "bin/tcsh":
            interpreter = "tcsh"
        elif magic_cookie[-7:] == "bin/csh":
            interpreter = "csh"
        else:
            interpreter = "sh"

        # コマンド文字列の作成
        if os.getuid() != user_id:
            command_args = ["su","-s", "/bin/bash", user, fname]
        else:
            command_args = [interpreter,fname]

        # コマンドの実行
        append_line(logfile,"[%s] Execute command '%s'." % (func_name," ".join(command_args),))
        (rc,res) = execute_command(command_args)
        new_res = []
        for _aline in res:
            append_line(logfile,"[%s] output> %s" % (func_name,_aline,))
            _aline = re.sub("^%s:[ \t]+" % fname, "", _aline)
            new_res.append(_aline)
            pass
        append_line(logfile,"[%s] command return value = %d" % (func_name,rc,))

        os.unlink(fname)

        retval = [rc,new_res]
    else:
        append_line(logfile,"[%s] Error: cannot create script file." % (func_name,))

    append_line(logfile,"[%s] Leaving function '%s'." % (func_name,func_name,))
    return retval

if __name__ == '__main__':
    """Testing
    """

    script = """#!/usr/bin/env python
import time
print time.strftime("%c", time.localtime(time.time()))
print '%{watch_name}'
print '%{msg}'
"""

    script = """#!/bin/sh

logfile="/tmp/exec_script.log"
whoami                >${logfile}
id                   >>${logfile}
echo '%{watch_name}' >>${logfile}
echo '%{msg}'        >>${logfile}
exit 0
"""
    user       = "kss"
    watch_name = u'\u30e1\u30e2\u30ea\u4f7f\u7528\u91cf\u3067\u3059'
    alert_msg  = u"foo blahhh"
    logfile = "/dev/stdout"

    exec_script(script=script,user=user,msg=alert_msg,watch_name=watch_name,logfile=logfile)
    pass

