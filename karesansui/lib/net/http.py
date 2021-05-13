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

import socket
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import base64
import logging
import traceback

import karesansui
from karesansui.lib.utils import is_empty

def is_ssl(hostname, port=443):
    """<comment-ja>
    指定したホスト:ポートがSSLに対応しているか調べる。

    @param hostname: ホスト名
    @type hostname: str
    @param port: ポート番号
    @type port: int
    @return: SSL対応=True | SSL非対応=False
    @rtype: bool
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.settimeout(5.0)
        _s.connect((hostname, port))
        if socket.ssl(_s):
            return True
        else:
            return False
    except:
        return False

def is_proxy(config):
    """<comment-ja>
    設定ファイルに設定しているProxy設定を利用できるか。

    @param config: 設定ファイル情報
    @type config: dict
    @return: 利用可=True | 利用不可=False
    @rtype: bool
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    if ("application.proxy.status" in config) is False:
        return False
    
    if config["application.proxy.status"] == "1":
        return True

    return False

def get_proxy(config):
    if is_proxy(config) is False:
        return None

    host = None
    port = None
    if ("application.proxy.server" in config) is True:
        host = config["application.proxy.server"]

    if ("application.proxy.port" in config) is True:
        port = config["application.proxy.port"]

    if is_empty(host) is True:
        return None, None

    return host, port

def get_proxy_user(config):
    if is_proxy(config) is False:
        return None

    user = ""
    password = ""

    if ("application.proxy.user" in config) is True:
        user = config["application.proxy.user"]

    if ("application.proxy.password" in config) is True:
        password = config["application.proxy.password"]

    if is_empty(user) is True:
        return None, None

    return user, password

def proxies(proxy_host, proxy_port, user=None, password=None, method="http"):

    if is_empty(user) is False and is_empty(password) is False \
           and is_empty(proxy_host) is False and is_empty(proxy_port) is False:

        return {method: "%s://%s:%s@%s:%s" \
                % (method,user,password,proxy_host,proxy_port)}

    elif is_empty(user) is False and is_empty(proxy_host) is False \
             and is_empty(proxy_port) is False:

        return {method: "%s://%s:@%s:%s" % (method,user,proxy_host,proxy_port)}

    elif is_empty(proxy_host) is False and is_empty(proxy_port) is False:
        return {method: "%s://%s:%s" % (method,proxy_host,proxy_port)}

    elif is_empty(proxy_host) is False:
        return {method: "%s://%s" % (method,proxy_host)}

    else:
        return None

def _wget_proxy(url, file, proxy_host, proxy_port, user=None, password=None):
    _proxies = proxies(proxy_host, proxy_port, user, password)
    if _proxies is None:
        return False

    try:
        proxy_handler = urllib.request.ProxyHandler(_proxies)
        auth_handler = urllib.request.ProxyBasicAuthHandler()
        opener = urllib.request.build_opener(proxy_handler, auth_handler)
        urllib.request.install_opener(opener)
        response = urllib.request.urlopen(url)

        fp = open(file, "w")
        try:
            fp.write(response.read())
        finally:
            fp.close()

        return True
    except Exception as e:
        logger_trace = logging.getLogger('karesansui_trace.net.http')
        logger_trace.error(traceback.format_exc())
        return False

def wget(url, file=None, proxy_host=None, proxy_port=None, proxy_user=None, proxy_password=None):
    logger = logging.getLogger('karesansui.net.http')
    if file == None:
        i = url.rfind('/')
        file = url[i+1:]

    if proxy_host is not None:
        logger.info("proxy connect - %s:%s (user,password)=(%s:xxxx) url=%s" % (proxy_host, proxy_port, proxy_user, url))
        if proxy_port is None:
            proxy_port = "8080"
        return _wget_proxy(url, file, proxy_host, proxy_port, proxy_user, proxy_password)

    elif is_proxy(karesansui.config) is True:
        proxy_host, proxy_port = get_proxy(karesansui.config)
        user, password = get_proxy_user(karesansui.config)
        logger.info("proxy connect - %s:%s (user,password)=(%s:xxxx) url=%s" % (proxy_host, proxy_port, user, url))
        return _wget_proxy(url, file, proxy_host, proxy_port, user, password)

    else:
        logger.info("not proxy connect - %s" % (url))
        urllib.request.urlretrieve(url, file)
        return True

