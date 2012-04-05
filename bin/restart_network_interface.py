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
import logging
import fcntl
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command
    from karesansui.lib.const import NETWORK_COMMAND

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    return optp.parse_args()

def chkopts(opts):
    return True

class RestartNetworkInterface(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        network_restart_cmd = (NETWORK_COMMAND,
                               "restart",
                               )
        (rc, res) = execute_command(network_restart_cmd)
        if rc != 0:
            raise KssCommandException('Failure restart network.')

        return True

if __name__ == "__main__":
    target = RestartNetworkInterface()
    sys.exit(target.run())
