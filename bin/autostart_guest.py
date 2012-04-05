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

class AutostartGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)
            flag = None
            if opts.enable:
                flag = True
            if opts.disable:
                flag = False
            self.up_progress(10)
            ret = conn.autostart_guest(flag)
            self.up_progress(40)
        finally:
            conn.close()

        if ret is False:
            raise KssCommandException('Failed to set autostart flag. - dom=%s flag=%s' \
                              % (opts.name,flag))

        self.logger.info('Set autostart flag. - dom=%s flag=%s' \
                         % (opts.name,flag))
        print >>sys.stdout, _('Set autostart flag. - dom=%s flag=%s') \
              % (opts.name,flag)
        return True

if __name__ == "__main__":
    target = AutostartGuest()
    sys.exit(target.run())
