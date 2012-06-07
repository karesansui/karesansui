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
    from karesansui.lib.const import ISCSI_CMD, ISCSI_CMD_OPTION_MODE, \
        ISCSI_CMD_OPTION_MODE_NODE, ISCSI_CMD_OPTION_OPERATOR, ISCSI_CMD_OPTION_OPERATOR_DELETE, \
        ISCSI_CMD_OPTION_TARGETNAME, ISCSI_CMD_OPTION_PORTAL

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

class DeleteIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        delete_command_args = [
            ISCSI_CMD,
            ISCSI_CMD_OPTION_MODE,
            ISCSI_CMD_OPTION_MODE_NODE,
            ISCSI_CMD_OPTION_OPERATOR,
            ISCSI_CMD_OPTION_OPERATOR_DELETE,
            ISCSI_CMD_OPTION_TARGETNAME,
            opts.iqn,
            ]
        if opts.host:
            delete_command_args.append(ISCSI_CMD_OPTION_PORTAL)
            delete_command_args.append(opts.host)

        (delete_rc,delete_res) = execute_command(delete_command_args)
        self.up_progress(50)

        if delete_rc != 0:
            raise KssCommandException('Failed to delete iSCSI. - host=%s iqn=%s message=%s' % (opts.host, opts.iqn, delete_res))

        self.logger.info("Delete iSCSI node successful. - host=%s iqn=%s" % (opts.host, opts.iqn))
        print >>sys.stdout, _("Delete iSCSI node successful. - host=%s iqn=%s") % (opts.host, opts.iqn)

        return True

if __name__ == "__main__":
    target = DeleteIscsi()
    sys.exit(target.run())
