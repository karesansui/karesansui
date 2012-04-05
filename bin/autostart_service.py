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
import re
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale
    from karesansui.lib.service.config import ServiceConfigParam
    from karesansui.lib.service.sysvinit_rh import SysVInit_RH
    from karesansui.lib.const import SERVICE_XML_FILE

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Service name'), default=None)
    optp.add_option('-e', '--enable', dest='enable', action="store_true", help=_('Enable autostart'), default=False)
    optp.add_option('-d', '--disable', dest='disable', action="store_true", help=_('Disable autostart'), default=False)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.enable is False and opts.disable is False:
        raise KssCommandOptException('ERROR: either %s options must be specified.' % '--enable or --disable')
    if opts.enable is True and opts.disable is True:
        raise KssCommandOptException('ERROR: %s options are conflicted.' % '--enable and --disable')

class AutostartService(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        config = ServiceConfigParam(SERVICE_XML_FILE)
        config.load_xml_config()

        service = config.findby1service(opts.name)
        if service is None:
            raise KssCommandException("Service not found in xml file. service=%s" % (opts.name))

        self.up_progress(10)
        sysv = SysVInit_RH(service['system_name'], service['system_command'])

        flag = None
        if opts.enable:
            flag = True
        if opts.disable:
            flag = False

        retval = sysv.onboot(flag)
        if not(retval is False) and not(retval is True):
            raise KssCommandException(str(sysv.error_msg))

        self.up_progress(50)
        if flag is True:
            message = 'Enable service. - service=%s' % (opts.name)
        else:
            message = 'Disable service. - service=%s' % (opts.name)

        self.logger.info(message)
        print >>sys.stdout, _(message)

        return True

if __name__ == "__main__":
    target = AutostartService()
    sys.exit(target.run())
