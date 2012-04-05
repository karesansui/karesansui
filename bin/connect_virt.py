#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import os
import sys
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, \
                 VIR_DOMAIN_SHUTOFF, VIR_DOMAIN_SHUTDOWN
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-c', '--count', dest='count', type="int", help=_('Connection Trial Count'), default=1)
    return optp.parse_args()

def chkopts(opts):
    try:
        int(opts.count)
    except:
        raise KssCommandOptException('ERROR: -c or --count option must be specified as a positive integer.')

class ConnectVirt(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        step = 100 / opts.count

        for cnt in xrange(0,opts.count):
            self.up_progress(step)
            try:
                print cnt
                conn = KaresansuiVirtConnection(readonly=False)
                print conn
            finally:
                pass
                #conn.close()

if __name__ == "__main__":
    target = ConnectVirt()
    sys.exit(target.run())
