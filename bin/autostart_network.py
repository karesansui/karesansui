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
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-e', '--enable', dest='enable', action="store_true", help=_('Enable autostart'))
    optp.add_option('-d', '--disable', dest='disable', action="store_true", help=_('Disable autostart'))
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.enable is None and opts.disable is None:
        raise KssCommandOptException('ERROR: either %s options must be specified.' % '--enable or --disable')

    if opts.enable is not None and opts.disable is not None:
        raise KssCommandOptException('ERROR: %s options are conflicted.' % '--enable and --disable')

class AutostartNetwork(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.network.set_network_name(opts.name)
            flag = None

            if opts.enable is True:
                flag = True
            elif opts.disable is True:
                flag = False
            else:
                raise KssCommandException('either %s options must be specified.' % '--enable or --disable')

            self.up_progress(10)
            ret = conn.autostart_network(flag)
            if ret is False:
                raise KssCommandException('Failed to set autostart flag. - net=%s flag=%s' % (opts.name,flag))
            self.up_progress(40)

            self.logger.info('Set autostart flag. - net=%s flag=%s' % (opts.name,flag))
            print >>sys.stdout, _('Set autostart flag. - net=%s flag=%s') % (opts.name,flag)

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = AutostartNetwork()
    sys.exit(target.run())
