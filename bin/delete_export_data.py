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
import os.path
import sys
import shutil
import glob
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, KaresansuiVirtException
    from karesansui.lib.utils import load_locale, is_uuid
    from karesansui.lib.virt.config_export import ExportConfigParam
    from karesansui.lib.virt.config import ConfigParam
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-u', '--uuid',  dest='uuid',  help=_('Export Data UUID'))

    return optp.parse_args()

def chkopts(opts):
    if opts.uuid:
        if not is_uuid(opts.uuid):
            raise KssCommandOptException('ERROR: Illigal UUID. uuid=%s' % (opts.uuid))
    else:
        raise KssCommandOptException('ERROR: -u or --uuid option is required.')

class DeleteExportData(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        kvc = KaresansuiVirtConnection()
        # #1 libvirt process
        try:
            #inactive_pool = kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            export = []
            for pool_name in pools:
                pool = kvc.search_kvn_storage_pools(pool_name)
                path = pool[0].get_info()["target"]["path"]
                if os.path.exists(path):
                    for _afile in glob.glob("%s/*/info.dat" % (path,)):
                        e_param = ExportConfigParam()
                        e_param.load_xml_config(_afile)

                        if e_param.get_uuid() != opts.uuid:
                            continue

                        e_name = e_param.get_domain()
                        _dir = os.path.dirname(_afile)

                        param = ConfigParam(e_name)

                        path = "%s/%s.xml" % (_dir, e_name)
                        if os.path.isfile(path) is False:
                            raise KssCommandException(
                                'Export corrupt data.(file not found) - path=%s' % path)

                        param.load_xml_config(path)

                        if e_name != param.get_domain_name():
                            raise KssCommandException(
                                'Export corrupt data.(The name does not match) - info=%s, xml=%s' \
                                % (e_name, param.get_name()))

                        _dir = os.path.dirname(_afile)

                        export.append({"dir" : _dir,
                                       "pool" : pool_name,
                                       "uuid" : e_param.get_uuid(),
                                       "name" : e_name,
                                       })

            if len(export) < 1:
                # refresh pool.
                conn = KaresansuiVirtConnection(readonly=False)
                try:
                    conn.refresh_pools()
                finally:
                    conn.close()
                raise KssCommandException('libvirt data did not exist. - uuid=%s' % opts.uuid)
            else:
                export = export[0]

        finally:
            kvc.close()

        self.up_progress(30)
        # #2 physical process
        if os.path.isdir(export['dir']) is False:
            raise KssCommandException(_("Failed to delete export data. - %s") % (_("Export data directory not found. [%s]") % (export['dir'])))

        uuid = os.path.basename(export['dir'])
        pool_dir = os.path.dirname(export['dir'])

        if not is_uuid(export['uuid']):
            raise KssCommandException(_("Failed to delete export data. - %s") % (_("'%s' is not valid export data directory.") % (export['dir'])))

        shutil.rmtree(export['dir'])

        for _afile in glob.glob("%s*img" % (export['dir'])):
            os.remove(_afile)

        self.up_progress(30)
        # refresh pool.
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            try:
                conn.refresh_pools()
            finally:
                conn.close()
        except:
            pass

        self.logger.info('Deleted export data. - uuid=%s' % (opts.uuid))
        print >>sys.stdout, _('Deleted export data. - uuid=%s') % (opts.uuid)
        return True

if __name__ == "__main__":
    target = DeleteExportData()
    sys.exit(target.run())
