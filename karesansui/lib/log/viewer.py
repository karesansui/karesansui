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
@author: Hiroki Takayasu <hiroki@karesansui-project.info>
"""
import re
import time
import datetime
import os
import os.path
import gzip
import fcntl

try:
  from hashlib import sha1 as sha
except:
  import sha
  from sha import sha

from karesansui.lib.const import DEFAULT_DATE_FORMAT, LOG_SYSLOG_REGEX, LOG_EPOCH_REGEX
from karesansui.lib.utils import reverse_file

def read_all_log(log_configs, max_line, start_datetime="", end_datetime="", keyword=""):
    lines = []
    max_line = int(max_line)

    for log_config in log_configs["logs"]:

        try:
            log_config['filepath']
        except:
            if log_config['dir'] is None:
                log_dir = "/var/log"
            else:
                if log_config['dir'][0] == "/":
                    log_dir = log_config['dir']
                else:
                    log_dir = "/var/log/%s" % log_config['dir']
            log_config['filepath'] = "%s/%s" % (log_dir, log_config["filename"])

        filepath = time.strftime(log_config['filepath'])

        if os.path.isfile(filepath) is False:
            continue

        one_file_lines = read_log(filepath, max_line, log_config, start_datetime, end_datetime, keyword)
        lines = one_file_lines + lines

        if len(lines) >= max_line and max_line != 0:
            break

    return lines[-max_line:]

def read_log_with_rotate(filename, max_line, log_config, start_datetime="", end_datetime="", keyword=""):
    if not filename: return False
    if not log_config: return False

    log_dir = "/var/log/%s" % log_config['dir']
    log_dir_list = [filename]
    max_line = int(max_line)

    for tmp_filename in os.listdir(log_dir):
        if tmp_filename.startswith(filename) and tmp_filename != filename:
            log_dir_list.append(tmp_filename)
    log_dir_list.sort()

    lines = []
    for read_filename in log_dir_list:
        log_path = "%s/%s" % (log_dir, read_filename)
        if os.path.isfile(log_path) is False:
            return False
        lines += read_log(log_path, max_line, log_config, start_datetime, end_datetime, keyword)
        if len(lines) >= max_line:
            return lines[:max_line]

    if len(lines) <= max_line:
        return lines
    else:
        return lines[:max_line]

def is_gzip(fd):
    fd.seek(0)
    header = fd.read(2)
    fd.seek(0)
    
    if header == '\x1f\x8b':
        ## GZIP形式
        return 1
    else:
        return 0

def read_log(path, max_line, log_config, start_datetime="", end_datetime="", keyword=""):
    if os.path.isfile(path) is False:
        return False

    time_format = log_config["time_format"]
    if start_datetime:
        start_datetime = time.strptime(start_datetime, DEFAULT_DATE_FORMAT[3])
        if time_format == "syslog":
            start_datetime = datetime.datetime.fromtimestamp(time.mktime(start_datetime)).timetuple()
    if end_datetime:
        end_datetime = time.strptime(end_datetime, DEFAULT_DATE_FORMAT[3])

        if time_format == "syslog":
            end_datetime = datetime.datetime.fromtimestamp(time.mktime(end_datetime)).timetuple()

    if log_config.get("time_pattern"):
        pattern = re.compile(log_config["time_pattern"])
    elif time_format == "epoch":
        pattern = re.compile(LOG_EPOCH_REGEX)
    elif time_format == "syslog":
        pattern = re.compile(LOG_SYSLOG_REGEX)
    elif time_format == "notime":
        pattern = None
    else:
        raise Exception("invalid time_format.")


    try:
        fd = open(path, "r")
    except Exception as e:
        raise
        
    if is_gzip(fd):
        fd.close()
        fd = gzip.open(path, "r")

    # ログの読み込み
    lines = []
    max_line = int(max_line)

    fd = file(path)
    if is_gzip(fd):
        fd = gzip.open(path, "r")
    fd = reverse_file(fd)
    fcntl.lockf(fd.fileno(), fcntl.LOCK_SH)
    try:
        count_line = 0
        for line in fd:
            if count_line >= max_line and max_line != 0:
                break

            if keyword and line.find(keyword) == -1:
                continue

            if time_format == "notime":
                lines.append(line)
                count_line += 1
            else:
                matched = pattern.findall(line)
                if len(matched) > 0:
                    if time_format == "epoch":
                        log_datetime = time.localtime(float(matched[0]))
                        _d = datetime.datetime(
                                log_datetime.tm_year,
                                log_datetime.tm_mon,
                                log_datetime.tm_mday,
                                log_datetime.tm_hour,
                                log_datetime.tm_min,
                                log_datetime.tm_sec)
                        view_datetime = _d.strftime("%Y/%m/%d %H:%M")
                        line = pattern.sub(view_datetime, line)
                    elif time_format == "syslog":
                        log_datetime = time.strptime("2000 %s" % matched[0], "%Y %b %d %H:%M:%S")
                    elif time_format == "notime":
                        log_datetime = 0.0
                    else:
                        log_datetime = time.strptime(matched[0], time_format)

                    if start_datetime and start_datetime > log_datetime:
                        break # check new logtime

                    if end_datetime and end_datetime < log_datetime:
                        continue

                    if (start_datetime and start_datetime <= log_datetime) or not start_datetime:
                        lines.append(line)
                        count_line += 1
                else:
                    ## timestamp not found.
                    lines.append(line)
                    count_line += 1
    finally:
        fcntl.lockf(fd.fileno(), fcntl.LOCK_UN)
        fd.close()
    lines.reverse()
    return lines

