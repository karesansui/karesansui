#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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


 使用方法: add_disk.py [オプション]

  オプション:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -t HOST, --target=HOST
                        ターゲットホスト名
  -a AUTH, --auth=AUTH  認証タイプ
  -u USER, --user=USER  認証ユーザー名
  -p PASSWORD, --password=PASSWORD
                        認証パスワード
  -w PASSWORD_FILE, --password-file=PASSWORD_FILE
                        認証パスワードファイル
  -s, --autostart       自動起動

</comment-ja>
<comment-en>
Attach a new disk device to the domain.

 usage: add_disk.py [options]

  options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -t HOST, --target=HOST
                        Target host name
  -a AUTH, --auth=AUTH  Authentication type
  -u USER, --user=USER  Authentication user name
  -p PASSWORD, --password=PASSWORD
                        Authentication password
  -w PASSWORD_FILE, --password-file=PASSWORD_FILE
                        Authentication password file
  -s, --autostart       Autostart

</comment-en>
"""

import os
import sys
import re
import logging
import fcntl
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command, is_readable
    from karesansui.lib.parser.iscsid import iscsidParser
    from karesansui.lib.dict_op import DictOp
    from karesansui.lib.iscsi import iscsi_parse_node, iscsi_print_format_node
    from karesansui.lib.const import ISCSI_CONFIG_KEY_AUTH_METHOD, ISCSI_CONFIG_KEY_AUTH_USER, \
        ISCSI_CONFIG_KEY_AUTH_PASSWORD, ISCSI_CONFIG_KEY_SATRTUP, ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, \
        ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE, ISCSI_CONFIG_VALUE_SATRTUP_ON, ISCSI_CONFIG_VALUE_SATRTUP_OFF, \
        ISCSI_CMD, ISCSI_CMD_OPTION_MODE, ISCSI_CMD_OPTION_MODE_DISCOVERY, ISCSI_CMD_OPTION_TYPE, \
        ISCSI_CMD_OPTION_TYPE_SENDTARGETS, ISCSI_CMD_OPTION_PORTAL

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-t', '--target', dest='host', help=_('Target host name'), default=None)
    optp.add_option('-a', '--auth', dest='auth', help=_('Authentication type'), default=None)
    optp.add_option('-u', '--user', dest='user', help=_('Authentication user'), default=None)
    optp.add_option('-p', '--password', dest='password', help=_('Authentication password'), default=None)
    optp.add_option('-w', '--password-file', dest='password_file', help=_('Authentication password file'), default=None)
    optp.add_option('-s', '--autostart', dest='autostart', action="store_true", help=_('Autostart'), default=False)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.host:
        if reg.search(opts.host):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-t or --target', opts.host))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-t or --target')

    if opts.auth:
        if not opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP and not opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE:
            raise KssCommandOptException('ERROR: %s option is require %s or %s.' % '-a', ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE)
        if opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP:
            if opts.user is None:
                raise KssCommandOptException('ERROR: %s option is required.' % '-u or --user')
            if opts.password is None and opts.password_file is None:
                raise KssCommandOptException('ERROR: %s option is required.' % '-p or --password or -w or --password-file')
            if opts.password_file is not None and not is_readable(opts.password_file):
                raise KssCommandOptException('ERROR: %s is not found.' % opts.password_file)
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-a or --auth')

class AddIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        original_parser = iscsidParser()
        new_parser = iscsidParser()
        dop = DictOp()

        dop.addconf("original", original_parser.read_conf())
        dop.addconf("new", new_parser.read_conf())

        self.up_progress(10)

        dop.cdp_set("new", ISCSI_CONFIG_KEY_AUTH_METHOD, opts.auth)
        if opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP:
            password = ""
            if opts.password is not None:
                password = opts.password
            elif opts.password_file is not None and is_readable(opts.password_file):
                try:
                    fp = open(opts.password_file, "r")
                    try:
                        fcntl.lockf(fp.fileno(), fcntl.LOCK_SH)
                        try:
                            password = fp.readline().strip("\n")
                        finally:
                            fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)

                        self.up_progress(10)
                    finally:
                        fp.close()

                except:
                    raise KssCommandException('Failed to read file. - target host=%s password_file=%s' \
                                                  % (opts.host,opts.password_file))

                try:
                    os.remove(opts.password_file)
                except:
                    raise KssCommandException('Failed to remove file. - target host=%s password_file=%s' \
                                                  % (opts.host,opts.password_file))

            dop.cdp_set("new", ISCSI_CONFIG_KEY_AUTH_METHOD, opts.auth)
            dop.cdp_set("new", ISCSI_CONFIG_KEY_AUTH_USER, opts.user)
            dop.cdp_set("new", ISCSI_CONFIG_KEY_AUTH_PASSWORD, password)
        else:
            dop.comment("new", ISCSI_CONFIG_KEY_AUTH_USER)
            dop.comment("new", ISCSI_CONFIG_KEY_AUTH_PASSWORD)

        self.up_progress(10)
        if opts.autostart:
            dop.cdp_set("new", ISCSI_CONFIG_KEY_SATRTUP, ISCSI_CONFIG_VALUE_SATRTUP_ON)
        else:
            dop.cdp_set("new", ISCSI_CONFIG_KEY_SATRTUP, ISCSI_CONFIG_VALUE_SATRTUP_OFF)

        new_parser.write_conf(dop.getconf("new"))
        self.up_progress(10)

        discovery_command_args = (ISCSI_CMD,
                                  ISCSI_CMD_OPTION_MODE,
                                  ISCSI_CMD_OPTION_MODE_DISCOVERY,
                                  ISCSI_CMD_OPTION_TYPE,
                                  ISCSI_CMD_OPTION_TYPE_SENDTARGETS,
                                  ISCSI_CMD_OPTION_PORTAL,
                                  opts.host
                                  )

        (discovery_rc,discovery_res) = execute_command(discovery_command_args)
        self.up_progress(10)

        original_parser.write_conf(dop.getconf("original"))
        self.up_progress(10)

        if discovery_rc != 0:
            raise KssCommandException('Failed to add iSCSI. - host=%s message=%s' % (opts.host, discovery_res))

        if discovery_res == []:
            raise KssCommandException('Failed to add iSCSI. - host=%s message=No exist permit iSCSI disk for target.' % (opts.host))

        for node_line in discovery_res:
            if not node_line:
                continue

            try:
                node = iscsi_parse_node(node_line)
            except:
                self.logger.warn('Failed to parse iSCSI discovery command response. message="%s"' % (node_line))
                continue

            self.logger.info("%s" % (iscsi_print_format_node(node)))
            print >>sys.stdout, _("%s") % (iscsi_print_format_node(node))

        return True

if __name__ == "__main__":
    target = AddIscsi()
    sys.exit(target.run())
