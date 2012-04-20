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

import re
from karesansui.lib.parser.iscsid import iscsidParser
from karesansui.lib.dict_op import DictOp
from karesansui.lib.const import ISCSI_DEFAULT_NODE_CONFIG_DIR, ISCSI_CONFIG_KEY_AUTH_METHOD, ISCSI_CONFIG_KEY_AUTH_USER, \
    ISCSI_CONFIG_KEY_SATRTUP, ISCSI_CONFIG_VALUE_SATRTUP_OFF

MODULE = "iscsi"

def _get_iscsi_config(node):
    path = iscsi_get_config_path_node(node)
    parser = iscsidParser()
    dop = DictOp()

    dop.addconf(MODULE, parser.read_conf(path))
    return dop

def iscsi_get_config_path_node(node):
    path = iscsi_get_config_path(
        node['hostname'],
        node['iqn'],
        node['port'],
        node['tpgt']
        )
    return path

def iscsi_get_config_path(hostname, iqn, port, tpgt):
    """
    <comment-ja>
    ノード別の設定ファイルパスを取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    path = ISCSI_DEFAULT_NODE_CONFIG_DIR + '/' + iqn + '/' + hostname + ',' + port + ',' + tpgt + '/default'

    return path

def iscsi_parse_node(line):
    """
    <comment-ja>
    iscsiadm -m node コマンドの情報をパースする
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    host,iqn = line.split(' ', 2)
    host,tpgt = host.split(',', 2)
    host,port = host.split(':', 2)
    node = {
        'hostname' : host,
        'port' : port,
        'tpgt' : tpgt,
        'iqn'  : iqn,
        }

    return node

def iscsi_parse_session(session):
    """
    <comment-ja>
    iscsiadm -m session コマンドの情報をパースする
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    protocol,id,host,iqn = session.split(' ', 4)
    protocol = protocol.replace(':','')
    id = re.search(r'\d+', id).group()
    host,tpgt = host.split(',', 2)
    host,port = host.split(':', 2)
    session = {
        'protocol' : protocol,
        'id'       : id,
        'hostname' : host,
        'tpgt'     : tpgt,
        'port'     : port,
        'iqn'      : iqn,
        }

    return session

def iscsi_print_format_node(node):
    return "%s %s %s %s" % (node['hostname'], node['port'], node['tpgt'], node['iqn'])

def iscsi_get_auth_type(node):
    """
    <comment-ja>
    ノードの認証タイプを取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    dop = _get_iscsi_config(node)
    return dop.cdp_get(MODULE, ISCSI_CONFIG_KEY_AUTH_METHOD)

def iscsi_get_auth_user(node):
    """
    <comment-ja>
    ノードの認証のユーザ名を取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    dop = _get_iscsi_config(node)
    user = dop.cdp_get(MODULE, ISCSI_CONFIG_KEY_AUTH_USER)
    if not user:
        user = ""

    return user

def iscsi_check_node_status(node, session):
    """
    <comment-ja>
    ノードが現在アクティブかどうか調べる
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if node['hostname'] == session['hostname'] and node['iqn'] == session['iqn']:
        is_active = True
    else:
        is_active = False

    return is_active

def iscsi_check_node_autostart(node):
    """
    <comment-ja>
    ノードの自動起動が有効かどうか調べる
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    dop = _get_iscsi_config(node)

    if dop.cdp_get(MODULE, ISCSI_CONFIG_KEY_SATRTUP).find(ISCSI_CONFIG_VALUE_SATRTUP_OFF):
        is_active = False
    else:
        is_active = True

    return is_active
