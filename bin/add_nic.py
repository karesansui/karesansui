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

from ksscommand import KssCommand, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, generate_mac_address
except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-m', '--mac', dest='mac', help=_('MAC Address'), default=None)
    optp.add_option('-b', '--bridge', dest='bridge', help=_('Bridge'), default=None)
    optp.add_option('-w', '--network', dest='network', help=_('Network'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.bridge is None and opts.network is None:
        raise KssCommandOptException('ERROR: either %s options must be specified.' % '--bridge or --network')
    """TOOD valid
    オプションチェック
    """

class AddNIC(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)

            self.up_progress(10)

            if not opts.mac:
                opts.mac = generate_mac_address()

            conn.guest.append_interface(opts.mac,opts.bridge,opts.network)
            self.up_progress(50)
        finally:
            conn.close()

        self.logger.info('Added interface device. - dom=%s mac=%s bridge=%s network=%s' \
                         % (opts.name, opts.mac, opts.bridge, opts.network))
        print >>sys.stdout, _('Added interface device. - dom=%s mac=%s bridge=%s network=%s') \
              % (opts.name, opts.mac, opts.bridge, opts.network)

        return True

if __name__ == "__main__":
    target = AddNIC()
    sys.exit(target.run())
