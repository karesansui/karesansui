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
@author: Hiroki Takayasu <hiroki@karesansui-project.info>
"""
import re
import time
import os
import os.path
try:
  from hashlib import sha1 as sha
except:
  import sha
  from sha import sha
import gzip

def read_all_log(app_log_config, max_line, start_datetime="", end_datetime="", keyword=""):
    lines = []
    logs = {}
    log_times = {}
    
    for log in app_log_config['logs']:
        log_path = "/var/log/%s/%s" % (log["dir"], log["filename"])
        if os.path.isfile(log_path) is False:
            return False
        lines = read_log(log_path, max_line, log, start_datetime, end_datetime, keyword)
        if lines is False:
            return False
        for line in lines:
            key = sha(line).hexdigest()
            logs.update({key: line})
            pattern = re.compile(log["time_pattern"])
            time_format = log["time_format"]
            now = time.strptime(pattern.findall(line)[0], time_format)
            log_times.update({key:int(time.mktime(now))})

    array = log_times.items()
    array.sort(key=lambda a:int(a[1]))
    lines = []
    for sorted_log in array[:max_line]:
        key = sorted_log[0]
        lines.append(logs.get(key))

    return lines

def read_log_with_lotate(filename, max_line, log_config, start_datetime="", end_datetime="", keyword=""):
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

    try:
        fd = open(path, "r")
    except Exception,e:
        raise
        
    if is_gzip(fd):
        fd.close()
        fd = gzip.open(path, "r")
    
    lines = []

    if start_datetime and end_datetime:
        start_datetime = time.strptime(start_datetime, "%Y/%m/%d %H:%M")
        end_datetime = time.strptime(end_datetime, "%Y/%m/%d %H:%M")

    line_flag = 0
    while True:
        time_format = log_config["time_format"]
        pattern = re.compile(log_config["time_pattern"])

        line = fd.readline()
        if not line:
            ## line is null. break while loop
            break
        if len(lines) >= int(max_line):
            break

        matched = pattern.findall(line)
        now = ""
        if len(matched):
            now = time.strptime(matched[0], time_format)
            line_flag = 1
        else:
            ## timestamp not found.
            if not line_flag:
                continue
            before_line = ""
            if len(lines):
                before_line = lines.pop()
            line = "%s%s" % (before_line, line)
            try:
                now = time.strptime(pattern.findall(line)[0], time_format)
            except:
                pass

        if start_datetime and end_datetime:
            if start_datetime >= now or end_datetime <= now:
                line_flag = 0
                continue
            
        if keyword:
            if line.find(keyword) > 0:
                lines.append(line)
        else:
            lines.append(line)
    fd.close()
    return lines
