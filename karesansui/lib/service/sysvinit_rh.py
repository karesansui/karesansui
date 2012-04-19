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

"""
 * 
 * System V 系 initスクリプトを利用してシステムサービスの起動制御を行う
 *
"""

import os
import sys
import time
import re
import glob
import signal

from karesansui.lib.utils import is_executable
from karesansui.lib.utils import execute_command
from karesansui.lib.utils import get_process_id

class SysVInit_RH:

    procdir           = "/proc"
    initrddir         = "/etc/init.d"
    piddir            = "/var/run"
    command_chkconfig = "/sbin/chkconfig"

    """
    <comment-ja>
    </comment-ja>
    <comment-en>
    </comment-en>
    """

    def __init__(self,name=None,path=None):
        """
        <comment-ja>
        @param self: -
        @return: なし
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """

        self.set_sleep_time(2)
        if name is not None:
            self.set_service_name(name)
        if path is not None:
            self.set_service_path(path)

        self.set_runlevel("3")

        self.error_msg = []
        pass

    def set_runlevel(self,runlevel="3"):
        self.runlevel = runlevel

    def set_sleep_time(self,seconds=2):
        self.sleep_time = seconds

    def set_service_name(self,name=None):
        """
        <comment-ja>
        制御対象サービス名をセットする
        @param self: -
        @param string name	制御対象サービス名
        @return: なし
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """

        self.service_name = name
        self.service_script = "%s/%s" % (self.initrddir, name,)

        return os.path.exists(self.service_script) and is_executable(self.service_script)


    def set_service_path(self,path=None):
        """
        <comment-ja>
        制御対象サービスの実行ファイル名をセットする
        @param self: -
        @param string path	制御対象サービスの実行ファイル名
        @return: なし
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """

        self.service_path = self._get_service_path(path)
        return os.path.exists(self.service_path) and is_executable(self.service_path)

    def _get_service_path(self,path=None):
        """
        <comment-ja>
        ベースネームの実行ファイル名から実行ファイルへの絶対パスを取得する
        @param self: -
        @param string path	実行ファイル名
        @return string		実行ファイルへの絶対パス
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """

        if path is None:
            path = self.service_name

        search_paths = [
            "/usr/share/karesansui/bin",
            "/usr/share/karesansui/sbin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
            "/usr/libexec",
            "/usr/libexec/postfix",
            "/usr/lib/courier-imap/libexec",
        ]

        if path[0:1] != "/":
            for _path in search_paths:
                _path = "%s/%s" % (_path,path,)
                if os.path.exists(_path) and is_executable(_path):
                    path = _path
                    break

        return path


    def status(self):
        """
        <comment-ja>
        制御対象サービスの現在の起動状態を取得する
        @param self: -
        @return mixed    起動中:サービスのPIDが格納された配列  停止中:[]
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        service_paths = "(%s|%s)" % (self.service_path,os.path.basename(self.service_path),)
        retval = get_process_id("^%s *(.+)?$" % service_paths, regex=True)

        # perl等を利用したデーモンはpidファイルで判定
        if len(retval) == 0:
            pid_file = "%s/%s.pid" % (self.piddir,self.service_name,)
            if os.path.exists(pid_file):
                try:
                    # 本当に起動しているか確かめよう
                    pids = open(pid_file).read().split()
                    for process_id in pids:
                        process_id = int(process_id)
                        cmdline_file = "%s/%d/cmdline" % (self.procdir,process_id,)
                        if os.path.exists(cmdline_file):
                            retval.append(process_id)
                except:
                    pass
        return retval

    def start(self,force=False):
        """
        <comment-ja>
        制御対象サービスを起動する
        @param self: -
        @return mixed   成功:サービスのPIDが格納された配列  失敗:False
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = False

        if force is False:
            pids = self.status()

        if force is True or len(pids) == 0:
            if os.path.exists(self.service_script) and is_executable(self.service_script):
                command = "%s start" % (self.service_script,)
                command_args = command.split()
                #print command
                (ret,res) = execute_command(command_args)

                time.sleep(self.sleep_time)
                if force is False:
                    pids = self.status()

                if force is False and len(pids) == 0:
                    message = "Error: failed to start '%s'." % (self.service_name,)
                    self.error_msg.append(message)
                else:
                    message = "Notice: succeeded to start '%s'." % (self.service_name,)
                    #print message
                    try:
                        retval = pids
                    except:
                        retval = True
            else:
                message = "Error: '%s' not found." % (self.service_script,)
                self.error_msg.append(message)
        else:
            pids = [str(p) for p, q in zip(pids, pids[1:] + [None])]
            message = "Warning: '%s' already running. [PID:%s]" % (self.service_name,",".join(pids),)
            self.error_msg.append(message)

        return retval

    def stop(self,force=False):
        """
        <comment-ja>
        制御対象サービスを停止する
        @param self: -
        @return boolean   成功:True  失敗:False
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = False

        if force is False:
            pids = self.status()

        if force is False and len(pids) == 0:
            message = "Warning: '%s' already stopped." % (self.service_name,)
            self.error_msg.append(message)

        else:
            if os.path.exists(self.service_script) and is_executable(self.service_script):
                command = "%s stop" % (self.service_script,)
                command_args = command.split()
                #print command
                (ret,res) = execute_command(command_args)

                time.sleep(self.sleep_time)
                if force is False:
                   pids = self.status()

                if force is True or len(pids) == 0:
                    message = "Notice: succeeded to stop '%s'." % (self.service_name,)
                    #print message
                    retval = True
                else:
                    pids = [str(p) for p, q in zip(pids, pids[1:] + [None])]
                    message = "Error: failed to stop '%s'. [%s]" % (self.service_name," ".join(res),)
                    self.error_msg.append(message)
                    message = "Notice: '%s' is running. [PID:%s]" % (self.service_name,",".join(pids),)
                    retval = False
            else:
                message = "Error: '%s' not found." % (self.service_script,)
                self.error_msg.append(message)

        return retval


    def restart(self,force=False):
        """
        <comment-ja>
        制御対象サービスを再起動する
        @param self: -
        @return mixed   成功:サービスのPIDが格納された配列  失敗:False
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = False

        retval = self.stop(force)
        retval = self.start(force)

        return retval


    def condrestart(self):
        """
        <comment-ja>
        制御対象サービスが起動中のときだけ再起動する
        @param self: -
        @return mixed   成功:サービスのPIDが格納された配列  失敗:False
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = True

        pids = self.status()
        if len(pids) != 0:
            retval = self.restart()

        return retval


    def reload(self):
        """
        <comment-ja>
        制御対象サービスにHUPシグナルを送る
        @param self: -
        @return boolean   成功:True  失敗:False
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = True

        pids = self.status()
        if len(pids) != 0:
            for _pid in pids:
                os.kill(_pid,signal.SIGHUP)

        return retval


    def onboot(self,flag=None,runlevel=None):
        """
        <comment-ja>
        制御対象サービスのマシン起動時の起動状態の有効/無効の切り替えを行う。
        または、その状態を取得する。
        @param self: -
        @param string flag 指定なし:状態を取得する
                           True    :起動時有効にする
                           False   :起動時無効にする
        @return boolean    True :状態取得なら起動時有効、起動時切替なら成功
                           False:状態取得なら起動時有効、起動時切替なら成功
        </comment-ja>
        <comment-en>
        constructor of class
        @param self: The object pointer
        @return: none
        </comment-en>
        """
        retval = False

        if flag is not None and flag is not True and flag is not False:
            raise Exception("Invalid argument.")

        if os.path.exists(self.service_script) and is_executable(self.service_script):
            script_name = os.path.basename(self.service_script)

            old_lang = os.environ["LANG"]
            os.environ["LANG"] = "C"

            if flag is None:
                command = "%s --list %s" % (self.command_chkconfig,script_name,)
                command_args = command.split()
                (ret,res) = execute_command(command_args)

                if runlevel is None:
                    runlevel = self.runlevel
                try:
                    m = re.search("[ \t]+%s:on[ \t]+" % runlevel ,res[0])
                    if m:
                        retval = True
                except:
                    pass

            else:
                if flag is True:
                    on_or_off = "on"
                else:
                    on_or_off = "off"
                if runlevel is None:
                    command = "%s %s %s" % (self.command_chkconfig,script_name,on_or_off)
                else:
                    command = "%s --level %s %s %s" % (self.command_chkconfig,runlevel,script_name,on_or_off)

                command_args = command.split()
                (ret,res) = execute_command(command_args)
                if ret == 0:
                    retval = True

            os.environ["LANG"] = old_lang

        else:
            message = "Error: '%s' not found." % (self.service_script,)
            self.error_msg.append(message)

        return retval
    
if __name__ == '__main__':
    """Testing
    """

    sysv = SysVInit_RH("libvirtd","libvirtd")
    print sysv.status()
    print sysv.onboot()
    print sysv.onboot(True)
    """
    print sysv.onboot()
    print sysv.onboot(False)
    print sysv.onboot()
    print sysv.onboot(True)
    print sysv.onboot()
    print "start"
    print sysv.start()
    print sysv.status()
    print sysv.reload()
    print sysv.status()
    print "stop"
    print sysv.stop()
    print sysv.status()
    print "start"
    print sysv.start()
    print sysv.status()

    sysv = SysVInit_RH("network","network")
    print sysv.status()
    print sysv.restart(force=True)
    """

    """
    sysv = SysVInit_RH("network","network")
    print sysv.onboot()
    print sysv.onboot(runlevel="4")
    """

    """
    sysv = SysVInit_RH("libvirtd","libvirtd")
    sysv.set_service_name("asynschedulerd")
    sysv.set_service_path("asynschedulerd.py")
    print sysv.status()
    """
