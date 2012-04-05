#!/usr/bin/python
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
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Storage pool name'))
    optp.add_option('-e', '--enable', dest='enable', action="store_true", help=_('Enable storage pool autostart'))
    optp.add_option('-d', '--disable', dest='disable', action="store_true", help=_('Disable storage pool autostart'))
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.enable is None and opts.disable is None:
        raise KssCommandOptException('ERROR: either %s options must be specified.' % '--enable or --disable')
    if opts.enable is not None and opts.disable is not None:
        raise KssCommandOptException('ERROR: %s options are conflicted.' % '--enable and --disable')

class AutostartStoragePool(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            inactive_storage_pools = conn.list_inactive_storage_pool()
            active_storage_pools = conn.list_active_storage_pool()
            self.up_progress(10)
            if not (opts.name in active_storage_pools or \
                    opts.name in inactive_storage_pools):
                raise KssCommandOptException('Storage pool does not exist. - pool=%s'
                                          % opts.name)

            conn.storage_pool.set_storage_name(opts.name)

            self.up_progress(10)
            flag = None
            if opts.enable:
                flag = True
            elif opts.disable:
                flag = False
            else:
                raise KssCommandException(
                    'ERROR: Execution status information does not exist. enable,disable=%s,%s' \
                    % (str(opts.enable), str(opts.disable)))

            self.up_progress(10)
            if conn.autostart_storage_pool(flag) is False:
                raise KssCommandException(
                    'Failed to autostart storage pool(libvirt). - pool=%s'
                    % (opts.name))

            ret = conn.is_autostart_storage_pool()
            if not (ret is flag):
                raise KssCommandException(
                    'Auto-start failed to set the storage pool. - pool=%s, autostart=%s' \
                    % (opts.name, str(ret)))

            self.up_progress(40)
            if opts.enable:
                self.logger.info('Set autostart storage pool. - pool=%s' % (opts.name))
                print >>sys.stdout, _('Set autostart storage pool. - pool=%s') % (opts.name)
            elif opts.disable:
                self.logger.info('Unset autostart storage pool. - pool=%s' % (opts.name))
                print >>sys.stdout, _('Unset autostart storage pool. - pool=%s') % (opts.name)

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = AutostartStoragePool()
    sys.exit(target.run())
