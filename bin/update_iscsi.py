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
    from karesansui.lib.iscsi import iscsi_get_config_path
    from karesansui.lib.const import ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE, \
        ISCSI_CONFIG_KEY_AUTH_METHOD, ISCSI_CONFIG_KEY_AUTH_USER, ISCSI_CONFIG_KEY_AUTH_PASSWORD, \
        ISCSI_CONFIG_KEY_SATRTUP, ISCSI_CONFIG_VALUE_SATRTUP_ON, ISCSI_CONFIG_VALUE_SATRTUP_OFF

except ImportError as e:
    print("[Error] some packages not found. - %s" % e, file=sys.stderr)
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-t', '--target', dest='host', help=_('Target host name'), default=None)
    optp.add_option('-i', '--iqn', dest='iqn', help=_('Target IQN'), default=None)
    optp.add_option('-P', '--port', dest='port', help=_('Target port number'), default="3260")
    optp.add_option('-T', '--tpgt', dest='tpgt', help=_('Target TPGT'), default="1")
    optp.add_option('-a', '--auth', dest='auth', help=_('Authentication type'), default=None)
    optp.add_option('-u', '--user', dest='user', help=_('Authentication user name'), default=None)
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

    if opts.iqn:
        if reg.search(opts.iqn):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-i or --iqn', opts.iqn))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-i or --iqn')

    if opts.auth:
        if not opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP and not opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE:
            raise KssCommandOptException('ERROR: %s option is require %s or %s.' % ('-a or --auth', ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP, ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE))
        if opts.auth == ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP:
            if opts.user is None:
                raise KssCommandOptException('ERROR: %s option is required.' % '-u or --user')
            if opts.password is None and opts.password_file is None:
                raise KssCommandOptException('ERROR: %s option is required.' % '-p or --password or -w or --password-file')
            if opts.password_file is not None and not is_readable(opts.password_file):
                raise KssCommandOptException('ERROR: %s is not found.' % opts.password_file)
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-a or --auth')

class UpdateIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        config_path = iscsi_get_config_path(opts.host, opts.iqn, opts.port, opts.tpgt)
        parser = iscsidParser()
        dop = DictOp()
        dop.addconf("new", parser.read_conf(config_path))

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

        self.up_progress(10)
        parser.write_conf(dop.getconf("new"), config_path)
        self.up_progress(30)

        self.logger.info("Updated iSCSI node. - host=%s iqn=%s" % (opts.host, opts.iqn))
        print(_("Updated iSCSI node. - host=%s iqn=%s") % (opts.host, opts.iqn), file=sys.stdout)

        return True

if __name__ == "__main__":
    target = UpdateIscsi()
    sys.exit(target.run())
