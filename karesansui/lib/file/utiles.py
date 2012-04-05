# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
