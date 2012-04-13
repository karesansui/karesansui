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
    optp.add_option('-s', '--memory', dest='memory', help=_('Memory size (MB)'), default=None)
    optp.add_option('-m', '--maxmem', dest='maxmem', help=_('Max memory size (MB)'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

class SetMemory(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        if opts.maxmem:
            opts.maxmem = str(opts.maxmem) + 'm'
        if opts.memory:
            opts.memory = str(opts.memory) + 'm'

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)

            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:
                try:
                    self.up_progress(10)
                    conn.guest.set_memory(opts.maxmem,opts.memory)
                    self.up_progress(20)
                    info = conn.guest.get_info()
                    self.up_progress(10)

                    self.logger.info('Set memory size. - dom=%s max=%d mem=%d' \
                                     % (opts.name, info['maxMem'], info['memory']))
                    print >>sys.stdout, _('Set memory size. - dom=%s max=%d mem=%d') \
                          % (opts.name, info['maxMem'], info['memory'])

                except Exception, e:
                    self.logger.error('Failed to set memory size. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to set memory size. - dom=%s') % (opts.name)
                    raise e

            else:
                raise KssCommandException('guest not found. - dom=%s' % (opts.name))

            return True
        finally:
            conn.close()


if __name__ == "__main__":
    target = SetMemory()
    sys.exit(target.run())
