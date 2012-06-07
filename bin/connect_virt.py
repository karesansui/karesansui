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

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
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
