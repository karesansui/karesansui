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
import time
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
    from karesansui.lib.utils import load_locale
    from karesansui.lib.utils import get_xml_parse        as XMLParse
    from karesansui.lib.utils import get_xml_xpath        as XMLXpath
    from karesansui.lib.utils import get_nums_xml_xpath   as XMLXpathNum
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
    #if not opts.id:
    #    raise KssCommandOptException('ERROR: -i or --id option is required.')

class TakeSnapshot(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        xml = None
        if opts.id:
            xml = "<domainsnapshot><name>%s</name></domainsnapshot>" % opts.id

        kvs = KaresansuiVirtSnapshot(readonly=False)
        try:
            self.up_progress(10)
            try:
                xmlDesc = kvs.createSnapshot(opts.name, xml)

                self.up_progress(50)
                if xmlDesc is not False:
                    doc = XMLParse(xmlDesc)
                    snapshot_name = XMLXpath(doc, '/domainsnapshot/name/text()')

                    msg = _("Domain snapshot '%s' created. - domain=%s") % (str(snapshot_name),opts.name,)
                    self.logger.info(msg)
                    print >>sys.stdout, msg
                else:
                    msg = _("Failed to create snapshot. - domain=%s") % (opts.name,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

            except KssCommandException, e:
                raise KssCommandException(''.join(e.args))
            except Exception, e:
                msg = _("Failed to create snapshot. - domain=%s") % (opts.name,)
                msg += ": detail %s" % ''.join(e.args)
                self.logger.error(msg)
                raise KssCommandException(msg)

        finally:
            kvs.finish()

        return True

if __name__ == "__main__":
    target = TakeSnapshot()
    sys.exit(target.run())
