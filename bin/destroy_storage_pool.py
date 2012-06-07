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
import re
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Storage pool name'))
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

class DestroyStoragePool(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            try:
                inactive_storage_pools = conn.list_inactive_storage_pool()
                active_storage_pools = conn.list_active_storage_pool()
                self.up_progress(10)
                if not (opts.name in active_storage_pools or \
                        opts.name in inactive_storage_pools):
                    raise KssCommandException('Storage pool does not exist. - pool=%s'
                                          % (opts.name))
                self.up_progress(30)

                if opts.name in conn.list_active_storage_pool():
                    if conn.destroy_storage_pool(opts.name) is False:
                        KssCommandException("Failed to stop the storage pool. - pool=%s"
                                            % (opts.name))
                else:
                    raise KssCommandException('Storage pool is not active. - pool=%s'
                                          % (opts.name))

                self.up_progress(30)

                # check
                if not (opts.name in conn.list_inactive_storage_pool()):
                    KssCommandException("Failed to stop the storage pool. - pool=%s"
                                        % (opts.name))

                self.logger.info('Stop storage pool. - pool=%s' % (opts.name))
                print >>sys.stdout, _('Stop storage pool. - pool=%s') % (opts.name)
                return True
            except KssCommandException, e:
                raise e
        finally:
            conn.close()

if __name__ == "__main__":
    target = DestroyStoragePool()
    sys.exit(target.run())
