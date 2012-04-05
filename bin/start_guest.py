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
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: -n or --name option is required.')

class StartGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)

            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:
                try:
                    self.up_progress(10)
                    conn.start_guest()
                    self.up_progress(30)
                except Exception, e:
                    self.logger.error('Failed to start guest. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to start guest. - dom=%s') % (opts.name)
                    raise e

                self.up_progress(10)
                status = conn.guest.status()
                self.up_progress(10)
                if status != VIR_DOMAIN_SHUTOFF and status != VIR_DOMAIN_SHUTDOWN:
                    self.logger.info('Succeeded to start guest. - dom=%s' % (opts.name))
                    print >>sys.stdout, _('Succeeded to start guest. - dom=%s') % (opts.name)

            else:
                raise KssCommandException(
                    'Guest not found. - dom=%s' % (opts.name))

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = StartGuest()
    sys.exit(target.run())
