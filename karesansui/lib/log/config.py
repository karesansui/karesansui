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
<comment-ja>
</comment-ja>
<comment-en>
Generate configuration file of logview.xml.
</comment-en>

@file:   config.py

@author: Hiroki Takayasu <hiroki@karesansui-project.info>
"""

import os
from StringIO import StringIO
from xml.dom.ext import PrettyPrint
from xml.dom.DOMImplementation import implementation
import errno
import re

import karesansui

from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_nums_xml_xpath as XMLXpathNum, \
     get_xml_parse as XMLParse, \
     uniq_filename, r_chgrp, r_chmod

from karesansui.lib.file.configfile import ConfigFile

class KaresansuiLogConfigParamException(karesansui.KaresansuiLibException):
    pass


class LogViewConfigParam:

    def __init__(self, path):
        self.applications = []
        self.path = path

    def findby1application(self, name):
        ret = None
        for application in self.get_applications():
            if application['name'] == name:
                ret = application

        return ret

    def add_application(self, name, logs):
        self.applications.append({"name" : name,
                                  "logs" : logs})

    def get_applications(self):
        return self.applications

    def load_xml_config(self, path=None):
        if path is not None:
            self.path = path

        if not os.path.isfile(self.path):
            raise KaresansuiLogConfigParamException(
                "logview.xml not found. path=%s" % str(self.path))

        document = XMLParse(self.path)

        self.applications = []
        
        app_num = XMLXpathNum(document, '/applications/application')
        for n in xrange(1, app_num + 1):
            app_name = XMLXpath(document, '/applications/application[%i]/name/text()' % n)
            logs = []
            logs_num = XMLXpathNum(document, '/applications/application[%i]/logs/log' % n)
            for i in xrange(1, logs_num + 1):
                log_name = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/name/text()' %
                                    (n, i))
                log_filename = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/filename/text()' %
                                    (n, i))
                log_filedir = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/dir/text()' %
                                    (n, i))
                view_rotatelog = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/view_rotatelog/text()' %
                                    (n, i))
                time_format = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/time_format/text()' %
                                       (n, i))
                time_pattern = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/time_pattern/text()' %
                                       (n, i))
                use_regex = XMLXpath(document, '/applications/application[%i]/logs/log[%i]/use_regex/text()' %
                                     (n, i))

                if int(use_regex):
                    for logfile in os.listdir("/var/log/%s/" % log_filedir):
                        pattern = re.compile("^%s$" % log_filename)
                        if pattern.findall(logfile):
                            logs.append({"name": logfile,
                                         "dir": log_filedir,
                                         "filename": logfile,
                                         "view_rotatelog":int(view_rotatelog),
                                         "time_format": str(time_format),
                                         "time_pattern": str(time_pattern),
                                         })
                else:
                    logs.append({"name": log_name,
                                 "dir": log_filedir,
                                 "filename": log_filename,
                                 "view_rotatelog":int(view_rotatelog),
                                 "time_format": str(time_format),
                                 "time_pattern": str(time_pattern),
                                 })
            
            self.add_application(str(app_name), logs)

