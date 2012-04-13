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

import os

import karesansui

from karesansui import KaresansuiException
from karesansui.lib.file.configfile import LighttpdSslConf
from karesansui.lib.const import LIGHTTPD_SSL_CONFIG,\
     LIGHTTPD_SSL_ON

def is_ssl():
    """
    <comment-ja>
    LighttpdがSSLを使用しているか判断する

    @return: bool
    </comment-ja>
    <comment-en>
    Judge whether Lighttpd uses SSL

    @return: bool
    </comment-en>
    """
    try:
        config = karesansui.config
        
        file_path = config['lighttpd.etc.dir'] + '/' + LIGHTTPD_SSL_CONFIG
        ssl_config_file = LighttpdSslConf(file_path)
        ssl_config = ssl_config_file.read()

        return ssl_config == LIGHTTPD_SSL_ON
    except Exception:
        raise KaresansuiException(_('Failed to read configuration file -%s') % file_path)
