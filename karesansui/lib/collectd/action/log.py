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
karesansui 警告ログを書き込む

引数2：ログ文字列
引数3：ログのレベルの重要度
"""

import os
import time
from karesansui.lib.collectd.utils import append_line
from karesansui.lib.const import COLLECTD_LOG_DIR

TIMESTAMP_FORMAT = "syslog"
TIMESTAMP_FORMAT = "Y-m-d"

COLLECTD_ALERT_LOG = "%s/alert.log" % COLLECTD_LOG_DIR

if TIMESTAMP_FORMAT == "syslog":
    COLLECTD_ALERT_LOG_TIMESTAMP_FORMAT = "%b %d %H:%M:%S"
else:
    COLLECTD_ALERT_LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S:"

def write_log(string,priority="WARNING"):

    priorities = [
              "DEBUG",
              "INFO",
              "OKAY",
              "WARNING",
              "FAILURE",
              ]

    rotate_log()

    # ログの書き込み
    msg = "%s [%s] %s" % (time.strftime(COLLECTD_ALERT_LOG_TIMESTAMP_FORMAT,time.localtime(time.time())),priority,string,)
    append_line(COLLECTD_ALERT_LOG,msg)

    return

def rotate_log(number=10,size=1024000):

    return

