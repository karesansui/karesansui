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
import os.path
import sys
import signal
import logging
from optparse import OptionParser
import glob

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, KaresansuiVirtException
    from karesansui.lib.utils import load_locale
    from karesansui.lib.virt.config_export import ExportConfigParam

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-e', '--exportuuid',  dest='exportuuid',  help=_('Export UUID to import'))
    optp.add_option('-d', '--destuuid', dest='destuuid', help=_('Guest UUID to import'))
    optp.add_option('-q', '--quiet',dest='verbose', action="store_false", default=True, help=_("don't print status messages"))

    return optp.parse_args()

def chkopts(opts):
    if not opts.exportuuid:
        raise KssCommandOptException('ERROR: -e or --exportuuid option is required.')
    if not opts.destuuid:
        raise KssCommandOptException('ERROR: -d or --destuuid option is required.')

class ImportGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            progresscb = None
            if opts.verbose:
                try:
                    from karesansui.lib.progress import ProgressMeter
                    progresscb = ProgressMeter(command_object=self)
                except:
                    pass
            else:
                try:
                    from karesansui.lib.progress import ProgressMeter
                    progresscb = ProgressMeter(command_object=self,quiet=True)
                except:
                    pass

            try:
                #inactive_pool = conn.list_inactive_storage_pool()
                inactive_pool = []
                active_pool = conn.list_active_storage_pool()
                pools = inactive_pool + active_pool
                if not pools:
                    raise KssCommandException("Storage pool does not exist, or has been stopped.")
                pools.sort()

                export = []
                for pool_name in pools:
                    pool = conn.search_kvn_storage_pools(pool_name)
                    path = pool[0].get_info()["target"]["path"]
                    if os.path.exists(path):
                        for _afile in glob.glob("%s/*/info.dat" % (path,)):
                            e_param = ExportConfigParam()
                            e_param.load_xml_config(_afile)

                            if e_param.get_uuid() != opts.exportuuid:
                                continue

                            export.append({"dir" : os.path.dirname(_afile),
                                           "uuid" : opts.exportuuid,
                                           })

                if len(export) != 1:
                    raise KssCommandException("There are differences in the export data and real data. - uuid=%s" % opts.exportuuid)
                else:
                    export = export[0]

                if os.path.isdir(export["dir"]) is False:
                    raise KssCommandException("There is no real data. - dir=%s" % export["dir"])

                conn.import_guest(export["dir"], uuid=opts.destuuid, progresscb=progresscb)

                self.up_progress(40)
                self.logger.info('Import guest completed. - export=%s, dest=%s' % (opts.exportuuid, opts.destuuid))
                print >>sys.stdout, _('Import guest completed. - export=%s, dest=%s' % (opts.exportuuid, opts.destuuid))
                return True

            except KaresansuiVirtException, e:
                raise KssCommandException('Failed to import guest. - [%s]' \
                                      % (''.join(str(e.args))))
        finally:
            conn.close()

if __name__ == "__main__":
    target = ImportGuest()
    sys.exit(target.run())
