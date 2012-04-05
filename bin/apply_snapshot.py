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

from ksscommand import KssCommand, KssCommandException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain name'))
    optp.add_option('-i', '--id', dest='id', help=_('Snapshot serial ID'))
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: -n or --name option is required.')
    if not opts.id:
        raise KssCommandOptException('ERROR: -i or --id option is required.')

class ApplySnapshot(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)


        kvs = KaresansuiVirtSnapshot(readonly=False)
        try:
            self.up_progress(10)
            try:

                domain = kvs.whichDomain(opts.id)
                if len(domain) == 0:
                    msg = _("Snapshot '%s' not found in domain '%s'.") % (opts.id,opts.name,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                if not opts.name in domain:
                    msg = _("Snapshot '%s' not found in domain '%s'.") % (opts.id,opts.name,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                ret = kvs.revertSnapshot(opts.id)
                if ret is False:
                    msg = _("Can't revert to snapshot '%s'.") % (opts.id,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                self.up_progress(50)

                msg = _("Domain snapshot '%s' reverted.") % (opts.id,)
                self.logger.info(msg)
                print >>sys.stdout, msg

            except KssCommandException, e:
                raise KssCommandException(''.join(e.args))

            except Exception, e:
                msg = _("Failed to revert to snapshot '%s'.") % (opts.id,)
                msg += ": detail %s" % ''.join(str(e.args))
                self.logger.error(msg)
                raise KssCommandException(msg)

            self.logger.info('Completed revertion to the snapshot - id=%s,name=%s' % (opts.id, opts.name))
            print >>sys.stdout, _('Completed revertion to the snapshot - id=%s,name=%s' % (opts.id, opts.name))
            return True
        finally:
            kvs.finish()

if __name__ == "__main__":
    target = ApplySnapshot()
    sys.exit(target.run())
