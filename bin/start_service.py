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
    from karesansui.lib.utils import load_locale
    from karesansui.lib.service.sysvinit_rh import SysVInit_RH
    from karesansui.lib.service.config import ServiceConfigParam
    from karesansui.lib.const import SERVICE_XML_FILE

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
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
