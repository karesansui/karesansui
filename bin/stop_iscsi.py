#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
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
    from karesansui.lib.const import ISCSI_CMD, ISCSI_CMD_OPTION_MODE, ISCSI_CMD_OPTION_MODE_NODE, \
        ISCSI_CMD_OPTION_TARGETNAME, ISCSI_CMD_OPTION_PORTAL, ISCSI_CMD_OPTION_LOGOUT

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
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

class StopIscsi(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        logout_command_args = [ISCSI_CMD,
                               ISCSI_CMD_OPTION_MODE,
                               ISCSI_CMD_OPTION_MODE_NODE,
                               ISCSI_CMD_OPTION_TARGETNAME,
                               opts.iqn,
                               ]
        if opts.host:
            logout_command_args.append(ISCSI_CMD_OPTION_PORTAL)
            logout_command_args.append(opts.host)

        logout_command_args.append(ISCSI_CMD_OPTION_LOGOUT)

        (logout_rc,logout_res) = execute_command(logout_command_args)
        self.up_progress(50)

        if logout_rc != 0:
            raise KssCommandException('Failed to logout iSCSI. - host=%s iqn=%s message=%s' % (opts.host, opts.iqn, logout_res))

        for line in logout_res:
            if not line:
                continue

            self.logger.info("%s" % (line))
            print >>sys.stdout, _("%s") % (line)

        return True

if __name__ == "__main__":
    target = StopIscsi()
    sys.exit(target.run())
