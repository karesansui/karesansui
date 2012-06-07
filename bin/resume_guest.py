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
                 VIR_DOMAIN_PAUSED
    from karesansui.lib.utils import load_locale

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
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

class ResumeGuest(KssCommand):

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
                    conn.resume_guest()
                    self.up_progress(30)
                except Exception, e:
                    self.logger.error('Failed to resume guest. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to resume guest. - dom=%s') % (opts.name)
                    raise e

                self.up_progress(10)
                status = conn.guest.status()
                self.up_progress(10)
                if status != VIR_DOMAIN_PAUSED:
                    self.logger.info('Succeeded to resume guest. - dom=%s' % (opts.name))
                    print >>sys.stdout, _('Succeeded to resume guest. - dom=%s') % (opts.name)

            else:
                self.logger.error('Guest not found. - dom=%s' % (opts.name))
                print >>sys.stderr, _('Guest not found. - dom=%s') % (opts.name)
                return False

            return True

        finally:
            conn.close()

if __name__ == "__main__":
    target = ResumeGuest()
    sys.exit(target.run())
