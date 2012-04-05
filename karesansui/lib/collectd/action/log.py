#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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

