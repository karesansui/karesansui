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
    from karesansui.lib.iscsi import iscsi_parse_node, iscsi_parse_session, iscsi_print_format_node, \
        iscsi_check_node_status, iscsi_check_node_autostart, iscsi_get_auth_type, iscsi_get_auth_user
    from karesansui.lib.const import ISCSI_CMD, ISCSI_CMD_OPTION_MODE, \
        ISCSI_CMD_OPTION_MODE_NODE, ISCSI_CMD_OPTION_MODE_SESSION, ISCSI_CMD_RES_NO_NODE, \
        ISCSI_CMD_RES_NO_ACTIVE_SESSION

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-i', '--iqn', dest='iqn', help=_('IQN'), default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\._:-]")

    if opts.iqn:
        if reg.search(opts.iqn):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-i or --iqn', opts.iqn))

class GetIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        node_command_args = (ISCSI_CMD,
                             ISCSI_CMD_OPTION_MODE,
                             ISCSI_CMD_OPTION_MODE_NODE
                             )

        (node_rc, node_res) = execute_command(node_command_args)
        if node_rc != 0:
            for node_line in node_res:
                if node_line.find(ISCSI_CMD_RES_NO_NODE) != -1:
                    self.logger.info("iSCSI node not found")
                    return True

            raise KssCommandException('Failed to get iSCSI node. message=%s' % (node_res))

        self.up_progress(20)
        session_command_args = (ISCSI_CMD,
                                ISCSI_CMD_OPTION_MODE,
                                ISCSI_CMD_OPTION_MODE_SESSION
                                )

        (session_rc, session_res) = execute_command(session_command_args)
        if session_rc != 0:
            raise KssCommandException('Failed to get iSCSI session. message=%s' % (session_res))

        self.up_progress(20)
        for node_line in node_res:
            if not node_line:
                continue

            try:
                node = iscsi_parse_node(node_line)
            except:
                self.logger.warn('Failed to parse iSCSI node command response. message="%s"' % (node_line))
                continue

            is_active = 0
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

                if iscsi_check_node_status(node, session):
                    is_active = 1
                    break

            if iscsi_check_node_autostart(node):
                autostart = 0
            else:
                autostart = 1

            if opts.iqn is None:
                self.logger.info("%s %s %s" % (iscsi_print_format_node(node), is_active, autostart))
                print >>sys.stdout, _("%s %s %s") % (iscsi_print_format_node(node), is_active, autostart)
            else:
                if opts.iqn == node['iqn']:
                    auth = iscsi_get_auth_type(node)
                    user = iscsi_get_auth_user(node)

                    self.logger.info("%s %s %s %s %s" % (iscsi_print_format_node(node), is_active, autostart, auth, user))
                    print >>sys.stdout, _("%s %s %s %s %s") % (iscsi_print_format_node(node), is_active, autostart, auth, user)
                    break

        return True

if __name__ == "__main__":
    target = GetIscsi()
    sys.exit(target.run())
