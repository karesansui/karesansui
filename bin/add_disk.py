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
    from karesansui.lib.utils import load_locale, get_disk_img_info
    from karesansui.lib.const import ISCSI_DEVICE_DIR, DISK_USES

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name',   dest='name',   help=_('Domain Name'),    default=None)
    #optp.add_option('-d', '--disk',   dest='disk',   help=_('Disk image file'), default=None)
    #optp.add_option('-s', '--size',   dest='size',   help=_('Disk size (MB)'), default=None)
    #optp.add_option('-p', '--sparse', dest='sparse', help=_('Sparse file'),    action="store_true")
    #optp.add_option('-t', '--target', dest='target', help=_('Device target'),  default=None)
    optp.add_option('-b', '--bus',    dest='bus',    help=_('Device type'),    default=None)
    #optp.add_option('-f', '--format', dest='format', help=_('Disk format'),    default=None)
    optp.add_option('-t', '--type',   dest='type',   help=_('Storage Type'),   default=None)
    optp.add_option('-p', '--pool',   dest='pool',   help=_('Storage Pool'),   default=None)
    optp.add_option('-v', '--volume', dest='volume', help=_('Storage Volume'), default=None)
    optp.add_option('-f', '--format', dest='format', help=_('Disk Format'),    default=None)
    optp.add_option('-T', '--target', dest='target',
                    help=_('Device name of your drive. example=hda or sda or vda...'))
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.pool:
        if reg.search(opts.pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool', opts.pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --pool')

    if opts.volume:
        if reg.search(opts.volume):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-v or --volume', opts.volume))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-v or --volume')

    if opts.type:
        if opts.type.lower() != "iscsi" and opts.type.lower() != "file":
            raise KssCommandOptException('ERROR: %s option is require %s or %s.' % ('-t or --type', 'iscsi', 'file'))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-t or --type')

    if opts.bus:
        if reg.search(opts.bus):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-b or --bus', opts.bus))

    if opts.format:
        if reg.search(opts.format):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-f or --format', opts.format))

    if opts.target:
        if reg.search(opts.target):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-f or --format', opts.target))

class AddDisk(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)
            self.up_progress(10)

            active_storage_pools = conn.list_active_storage_pool()
            if opts.pool not in active_storage_pools:
                raise KssCommandException('Storage pool does not exist. - pool=%s' % opts.name)

            if not conn.get_storage_volume(opts.pool, opts.volume):
                raise KssCommandException('Storage volume does not exist. - pool=%s, volume=%s' % (opts.name, opts.volume))

            self.up_progress(10)
            if opts.type.lower() == 'iscsi':
                real_volume_path = conn.get_storage_volume_iscsi_rpath_bystorage(opts.pool, opts.volume)
                if not real_volume_path:
                    raise KssCommandException('Failure get iSCSI volume real path. - pool=%s, volume=%s' % (opts.name, opts.volume))

                format = None
                disk_type = 'block'

            elif opts.type.lower() == 'file':
                real_volume_path = "%s/%s/%s/%s.img" % \
                                   (conn.get_storage_pool_targetpath(opts.pool),
                                    opts.name,
                                    DISK_USES["DISK"],
                                    opts.volume)
                format = opts.format
                disk_type = 'file'
            else:
                raise KssCommandException('Unknown Storage Type. type=%s' % opts.type)

            if opts.target:
                target = opts.target
            else:
                target = conn.guest.next_disk_target(opts.bus)

            self.up_progress(10)
            already_disks = conn.guest.get_disk_info()
            for already_disk in already_disks:
                if already_disk['type'] == 'file':
                    already_path = already_disk['source']['file']
                elif already_disk['type'] == 'block':
                    already_path = already_disk['source']['dev']
                else:
                    already_path = ''

                if already_path == real_volume_path:
                    raise KssCommandException('Source disk is already used. path=%s' % real_volume_path)

            if opts.format is None:
                format = get_disk_img_info(real_volume_path)['file_format']

            conn.guest.append_disk(real_volume_path,
                                   target,
                                   bus=opts.bus,
                                   disk_type=disk_type,
                                   driver_name=None,
                                   driver_type=format,
                                   )

            self.up_progress(30)
        finally:
            conn.close()

        self.logger.info('Added disk device. - dom=%s target=%s path=%s' \
                         % (opts.name, target, real_volume_path))
        print >>sys.stdout, 'Added disk device. - dom=%s target=%s path=%s' \
              % (opts.name, target, real_volume_path)

        return True

if __name__ == "__main__":
    target = AddDisk()
    sys.exit(target.run())
