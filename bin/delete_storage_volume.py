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
    from karesansui.lib.const import DISK_USES
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Storage volume name'), default=None)
    optp.add_option('-p', '--pool_name', dest='pool_name', help=_('Storage pool name'), default=None)
    optp.add_option('-U', '--use', dest='use',
                    help=_('Use of disk usage."images" or "disk"'), default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.pool_name:
        if reg.search(opts.pool_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool_name', opts.pool_name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --pool_name')

    if opts.use:
        if opts.use not in DISK_USES.values():
            raise KssCommandOptException('ERROR: Disk usage is not available. '
                                         'images or disk is available. use=%s' % opts.use)

class DeleteStorageVolume(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            inactive_storage_pools = conn.list_inactive_storage_pool()
            active_storage_pools = conn.list_active_storage_pool()
            self.up_progress(10)

            if not (opts.pool_name in active_storage_pools or \
                   opts.pool_name in inactive_storage_pools):
                raise KssCommandException('Storage pool does not exist. - pool=%s'
                                          % opts.name)

            pool_dir = conn.get_storage_pool_targetpath(opts.pool_name)
            #image_path = os.path.realpath("%s/%s/images/%s.img" % (pool_dir, opts.name, opts.name))
            #vol = conn.get_storage_volume_symlink(image_path)
            #if not vol:
            #    raise KssCommandException("Storage volume could not be found.")
            #else:
            #    vol = vol[0]

            if conn.get_storage_volume(opts.pool_name, opts.name) is None:
                raise KssCommandException(
                    'Specified storage volume does not exist. - pool=%s, vol=%s'
                    % (opts.pool_name, opts.name))

            try:
                self.up_progress(30)
                if conn.delete_storage_volume(opts.pool_name,
                                              opts.name,
                                              opts.use,
                                              True) is False:
                    KssCommandException("Failed to destroy storage volume. (libvirt)- pool=%s, vol=%s" \
                                        % (opts.pool_name, opts.name))

                self.up_progress(30)
                self.logger.info('Deleted storage volume. - pool=%s, vol=%s' % (opts.pool_name, opts.name))
                print >>sys.stdout, _('Deleted storage volume. - pool=%s, vol=%s') % (opts.pool_name, opts.name)
                return True
            except KssCommandException, e:
                raise e
        finally:
            conn.close()

if __name__ == "__main__":
    target = DeleteStorageVolume()
    sys.exit(target.run())
