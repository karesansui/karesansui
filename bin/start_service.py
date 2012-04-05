#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2010 HDE, Inc.
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
    from karesansui.lib.utils import load_locale
    from karesansui.lib.service.sysvinit_rh import SysVInit_RH
    from karesansui.lib.service.config import ServiceConfigParam
    from karesansui.lib.const import SERVICE_XML_FILE

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Service name'))
    return optp.parse_args()

def chkopts(opts):
    if opts.name is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

class StartService(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()

        service = config.findby1service(opts.name)
        if not service:
            raise KssCommandException("Could not find the service - name=%s" % opts.name)

        self.up_progress(10)
        sysv = SysVInit_RH(service['system_name'], service['system_command'])

        if sysv.start(force=False) is False:
            raise KssCommandException(str(sysv.error_msg))

        self.up_progress(50)
        self.logger.info('Started service. - service=%s' % (opts.name))
        print >>sys.stdout, _('Started service. - service=%s') % (opts.name)

        return True

if __name__ == "__main__":
    target = StartService()
    sys.exit(target.run())
