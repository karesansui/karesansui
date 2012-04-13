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

"""
<comment-ja>
Volumeがfile形式のみ実行可能です。
</comment-ja>
<comment-en>
You can only file format the volume.
</comment-en>
"""

import os
import os.path
import sys
import re
import signal
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, chk_create_disk
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)

    #optp.add_option('-u', '--uuid', dest='uuid', help=_('Destination UUID'))
    optp.add_option('-n', '--orig_name', dest='orig_name', help=_('Original Domain Name'))
    optp.add_option('-p', '--orig_pool', dest='orig_pool', help=_('Original storage pool'))
    optp.add_option('-v', '--orig_volume', dest='orig_volume', help=_('Original storage volume'))
    optp.add_option('-N', '--dest_name', dest='dest_name', help=_('Destination Domain Name'))
    optp.add_option('-P', '--dest_pool', dest='dest_pool', help=_('Destination storage pool'))
    optp.add_option('-V', '--dest_volume', dest='dest_volume', help=_('Destination storage volume'))
    optp.add_option('-d', '--debug', dest='debug', action="store_true",help=_('Debug Option'))

    return optp.parse_args()

def chkopts(opts):
    #if not opts.uuid:
    #    raise KssCommandOptException('ERROR: -u or --uuid option is required.')

    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.orig_name:
        if reg.search(opts.orig_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --orig_name', opts.orig_name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --orig_name')

    if opts.orig_pool:
        if reg.search(opts.orig_pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --orig_pool', opts.orig_pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --orig_pool')

    if opts.orig_volume:
        if reg.search(opts.orig_volume):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-v or --orig_volume', opts.orig_volume))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-v or --orig_volume')

    if opts.dest_name:
        if reg.search(opts.dest_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-N or --dest_name', opts.dest_name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-N or --dest_name')

    if opts.dest_pool:
        if reg.search(opts.dest_pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-P or --dest_pool', opts.dest_pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-P or --dest_pool')

    if opts.dest_volume:
        if reg.search(opts.dest_volume):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-V or --dest_volume', opts.dest_volume))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-V or --dest_volume')

class ReplicateStorageVolume(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            try:
                self.up_progress(10)
                progresscb = None
                if opts.debug is True:
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

                vol_obj = conn.get_storage_volume(opts.orig_pool, opts.orig_volume)
                if vol_obj is None:
                    raise KssCommandException(
                        'Specified storage volume does not exist. - pool=%s, vol=%s'
                        % (opts.orig_pool, opts.orig_volume))

                inactive_storage_pools = conn.list_inactive_storage_pool()
                active_storage_pools = conn.list_active_storage_pool()
                if not (opts.dest_pool in active_storage_pools or \
                            opts.dest_pool in inactive_storage_pools):
                    raise KssCommandException('Destination storage pool does not exist. - pool=%s'
                                              % (opts.dest_pool))

                vol_info = vol_obj.info()
                if vol_info[0] != 0:
                    raise KssCommandException(
                        'Specified storage volume does not "file" type. - pool=%s, vol=%s'
                        % (opts.orig_pool, opts.orig_volume))

                filesize = vol_info[1] / (1024 * 1024) # a unit 'MB'
                target_path = conn.get_storage_pool_targetpath(opts.dest_pool)
                if chk_create_disk(target_path, filesize) is False:
                    raise KssCommandException(
                        'Destination storage pool shortage capacity. - pool=%s'
                        % (opts.dest_pool))

                if conn.replicate_storage_volume(opts.orig_name,
                                                 opts.orig_pool,
                                                 opts.orig_volume,
                                                 opts.dest_name,
                                                 opts.dest_pool,
                                                 opts.dest_volume,
                                                 progresscb) is False:

                    raise KssCommandException(_("Failed to copy storage volume."))
                self.up_progress(40)
                self.logger.info('Replicate storage volume. - orig_pool=%s, orig_vol=%s, dest_pool=%s' % (opts.orig_pool, opts.orig_volume, opts.dest_pool))
                print >>sys.stdout, _('Replicate storage volume. - orig_pool=%s, orig_vol=%s, dest_pool=%s' % (opts.orig_pool, opts.orig_volume, opts.dest_pool))
                return True
            except Exception, e:
                raise e
        finally:
            conn.close()

if __name__ == "__main__":
    target = ReplicateStorageVolume()
    sys.exit(target.run())
