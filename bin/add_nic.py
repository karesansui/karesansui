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

from ksscommand import KssCommand, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, generate_mac_address
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain name'))
    optp.add_option('-m', '--mac', dest='mac', help=_('MAC address'), default=None)
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
