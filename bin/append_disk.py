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
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain name'))
    optp.add_option('-d', '--disk', dest='disk', help=_('Disk image file'))
    optp.add_option('-t', '--target', dest='target', help=_('Device target'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')
    if not opts.disk or not os.path.exists(opts.disk):
        raise KssCommandOptException('ERROR: disk image not found.')

class AppendDisk(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)

            self.up_progress(10)
            if not opts.target:
                opts.target = conn.guest.next_disk_target()

            conn.guest.append_disk(opts.disk,opts.target)
            self.up_progress(50)
        finally:
            conn.close()

        self.logger.info('Appended disk device. - dom=%s target=%s path=%s' \
                         % (opts.name, opts.target, opts.disk))
        print >>sys.stdout, _('Appended disk device. - dom=%s target=%s path=%s') \
              % (opts.name,opts.target,opts.disk)
        return True

if __name__ == "__main__":
    target = AppendDisk()
    sys.exit(target.run())
