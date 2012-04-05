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
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain name'))
    optp.add_option('-c', '--vcpus', dest='vcpus', help=_('Number of virtual CPUs'), default=None)
    optp.add_option('-m', '--max-vcpus', dest='max_vcpus', help=_('Maximum number of virtual CPUs'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

class SetVcpus(KssCommand):

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
                    conn.guest.set_vcpus(vcpus=opts.vcpus,max_vcpus=opts.max_vcpus)
                    self.up_progress(20)
                    info = conn.guest.get_vcpus_info()
                    self.up_progress(10)

                    self.logger.info('Set vcpus. - dom=%s vcpus=%s max_vcpus=%s bootup_vcpus=%s' \
                                     % (opts.name, info['vcpus'], info['max_vcpus'], info['bootup_vcpus']))
                    print >>sys.stdout, _('Set vcpus. - dom=%s vcpus=%s max_vcpus=%s bootup_vcpus=%s') \
                          % (opts.name, info['vcpus'], info['max_vcpus'], info['bootup_vcpus'])

                except Exception, e:
                    self.logger.error('Failed to set vcpus. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to set vcpus. - dom=%s') % (opts.name)
                    raise e

            else:
                raise KssCommandException('guest not found. - dom=%s' % (opts.name))

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = SetVcpus()
    sys.exit(target.run())
