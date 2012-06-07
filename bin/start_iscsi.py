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
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command
    from karesansui.lib.iscsi import iscsi_parse_session
    from karesansui.lib.const import ISCSI_CMD, \
        ISCSI_CMD_OPTION_MODE,       ISCSI_CMD_OPTION_MODE_SESSION, \
        ISCSI_CMD_OPTION_MODE_NODE,  ISCSI_CMD_OPTION_TARGETNAME, \
        ISCSI_CMD_OPTION_PORTAL,     ISCSI_CMD_OPTION_LOGIN, \
        ISCSI_CMD_RES_NO_ACTIVE_SESSION

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-t', '--target', dest='host', help=_('Target host name'), default=None)
    optp.add_option('-i', '--iqn', dest='iqn', help=_('Target IQN'), default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\._:-]")

    if opts.iqn:
        if reg.search(opts.iqn):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-i or --iqn', opts.iqn))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-i or --iqn')

    if opts.host:
        if reg.search(opts.host):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-t or --target', opts.host))

class StartIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        already_exist = False

        session_command_args = (ISCSI_CMD,
                                ISCSI_CMD_OPTION_MODE,
                                ISCSI_CMD_OPTION_MODE_SESSION
                                )

        (session_rc, session_res) = execute_command(session_command_args)
        if session_rc != 0:
            raise KssCommandException('Failed to get iSCSI session. message=%s' % (session_res))

        for session_line in session_res:
            if not session_line:
                continue

            if session_line.find(ISCSI_CMD_RES_NO_ACTIVE_SESSION) != -1:
                break

            try:
                session = iscsi_parse_session(session_line)
            except:
                self.logger.warn('Failed to parse iSCSI session command response. message="%s"' % (session_line))
                continue

            if session['iqn'] == opts.iqn:
                if opts.host:
                    if opts.host != session['hostname']:
                        continue
                already_exist = True
                break

        if already_exist:
            self.logger.info("[target: %s]: already exists" % (opts.iqn))
            print >>sys.stdout, _("[target: %s]: already exists") % (opts.iqn)
        else:
            login_command_args = [ISCSI_CMD,
                                  ISCSI_CMD_OPTION_MODE,
                                  ISCSI_CMD_OPTION_MODE_NODE,
                                  ISCSI_CMD_OPTION_TARGETNAME,
                                  opts.iqn,
                                  ]
            if opts.host:
                login_command_args.append(ISCSI_CMD_OPTION_PORTAL)
                login_command_args.append(opts.host)

            login_command_args.append(ISCSI_CMD_OPTION_LOGIN)

            (login_rc,login_res) = execute_command(login_command_args)
            self.up_progress(50)

            if login_rc != 0:
                raise KssCommandException('Failed to login to iSCSI. - host=%s iqn=%s message=%s' % (opts.host, opts.iqn, login_res))

            for line in login_res:
                if not line:
                    continue

                self.logger.info("%s" % (line))
                print >>sys.stdout, _("%s") % (line)

        return True

if __name__ == "__main__":
    target = StartIscsi()
    sys.exit(target.run())
