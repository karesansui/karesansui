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
import re
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, is_uuid, is_iso9660_filesystem_format
    from karesansui.lib.const import DEFAULT_KEYMAP, GRAPHICS_PORT_MIN_NUMBER, GRAPHICS_PORT_MAX_NUMBER

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    # basic
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-t', '--type', dest='type', help=_('VM Type'), default="xen")
    optp.add_option('-m', '--mem-size', dest='mem_size', help=_('Memory Size (MB)'), default=256)
    optp.add_option('-d', '--disk', dest='disk', help=_('Disk image file'), default=None)
    optp.add_option('-v', '--graphics-port', dest='graphics_port', help=_('Graphics Port Number'), default=None)
    optp.add_option('-u', '--uuid', dest='uuid', help=_('UUID'), default=None)
    optp.add_option('-a', '--mac', dest='mac', help=_('MAC Address'), default=None)
    optp.add_option('-c', '--vcpus', dest='vcpus', help=_('Number of virtual CPUs to allocate'), default=1)
    optp.add_option('-f', '--interface-format', dest='interface_format', help=_('Interface format'), default='b:xenbr0')
    optp.add_option('-b', '--keymap', dest='keymap', help=_('Graphics Keyboard Map'), default=DEFAULT_KEYMAP)
    optp.add_option('-e', '--extra', dest='extra', help=_('Extra kernel options'), default=None)
    # Storage pool only
    optp.add_option('-P', '--storage-pool', dest='storage_pool', help=_('Storage pool name'), default=None)
    optp.add_option('-V', '--storage-volume', dest='storage_volume', help=_('Storage volume name'), default=None)
    # make disk only
    optp.add_option('-D', '--disk-format', dest='disk_format', help=_('Disk format'), default=None)
    optp.add_option('-s', '--disk-size', dest='disk_size', help=_('Disk size (MB)'), default=1024*8)
    # IDE or SCSI or Virtio
    optp.add_option('-B', '--bus', dest='bus', help=_('Device bus type'), default=None)
    # ISO only
    optp.add_option('-o', '--iso', dest='iso', help=_('ISO image'), default=None)
    # Individual designation
    optp.add_option('-k', '--kernel', dest='kernel', help=_('Kernel image'), default=None)
    optp.add_option('-i', '--initrd', dest='initrd', help=_('initrd image'), default=None)

    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.type:
        if opts.type.lower() != "xen" and opts.type.lower() != "kvm":
            raise KssCommandOptException('ERROR: %s option is require %s or %s.' % ('-t or --type', 'xen', 'kvm'))

    if opts.storage_pool:
        if reg.search(opts.storage_pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-P or --storage-pool', opts.storage_pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-P or --storage-pool')

    if opts.storage_volume:
        if reg.search(opts.storage_volume):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-V or --storage-volume', opts.storage_volume))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-V or --storage-volume')

    if opts.bus:
        if reg.search(opts.bus):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-B or --bus', opts.bus))

    reg = re.compile("[^0-9]")
    if opts.mem_size:
        if reg.search(str(opts.mem_size)):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-m or --mem-size', opts.mem_size))

    if opts.graphics_port:
        if reg.search(str(opts.graphics_port)):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-v or --graphics-port', opts.graphics_port))
        elif int(opts.graphics_port) < GRAPHICS_PORT_MIN_NUMBER or GRAPHICS_PORT_MAX_NUMBER < int(opts.graphics_port):
            raise KssCommandOptException('ERROR: Illigal port number. option=%s value=%s' % ('-v or --graphics-port', opts.graphics_port))

    if opts.vcpus:
        if reg.search(str(opts.vcpus)):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-c or --vcpus', opts.vcpus))

    if opts.uuid:
        if not is_uuid(opts.uuid):
            raise KssCommandOptException('ERROR: Illigal UUID. uuid=%s' % (opts.uuid))

    if opts.mac:
        reg = re.compile("^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")
        if not reg.match(opts.mac):
            raise KssCommandOptException('ERROR: Illigal MAC address. mac=%s' % (opts.mac))

    #if opts.disk and os.path.isfile(opts.disk) is False:
    #    raise KssCommandOptException('ERROR: %s not found.' % opts.disk)

    if opts.iso is not None:
        if opts.kernel is not None or opts.initrd is not None:
            raise KssCommandOptException('ERROR: %s option cannot be specified with %s options.' % ('--iso', '--kernel and --initrd',))

        if os.path.isfile(opts.iso) is False:
            raise KssCommandOptException('ERROR: The specified ISO image path does not exist. - %s' % opts.iso)

        if is_iso9660_filesystem_format(opts.iso) is False:
            raise KssCommandOptException('ERROR: The specified ISO image is not valid ISO 9660 CD-ROM filesystem data. - %s' % opts.iso)

    else:
        _r_get_net = re.compile("^(ftp|http)://")

        if opts.kernel:
            if _r_get_net.match(str(opts.kernel)) is None and os.path.isfile(opts.kernel) is False:
                raise KssCommandOptException('ERROR: The specified kernel image path does not exist. - %s' % opts.kernel)
        else:
            raise KssCommandOptException('ERROR: %s option is required.' % '-k or --kernel')

        if opts.initrd:
            if _r_get_net.match(str(opts.initrd)) is None and os.path.isfile(opts.initrd) is False:
                raise KssCommandOptException('ERROR: The specified initrd image path does not exist. - %s' % opts.initrd)
        else:
            raise KssCommandOptException('ERROR: %s option is required.' % '-i or --initrd')

class CreateGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_interface_format(opts.interface_format)

            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:
                raise KssCommandException('Guest already exists. - dom=%s' % (opts.name))

            self.up_progress(10)
            inactive_storage_pools = conn.list_inactive_storage_pool()
            active_storage_pools = conn.list_active_storage_pool()
            if not (opts.storage_pool in active_storage_pools or opts.storage_pool in inactive_storage_pools):
                raise KssCommandException('Storage pool does not exist. - pool=%s' % (opts.storage_pool))

            # TODO
            #if conn.get_storage_volume(opts.storage_pool, opts.uuid) is None:
            #    raise KssCommandException('Specified storage volume does not exist. - pool=%s, vol=%s'
            #                              % (opts.storage_pool, opts.uuid))

            try:
                self.up_progress(10)
                if not conn.create_guest(name=opts.name,
                                         type=opts.type.lower(),
                                         ram=opts.mem_size,
                                         disk=opts.disk,
                                         disksize=opts.disk_size,
                                         mac=opts.mac,
                                         uuid=opts.uuid,
                                         kernel=opts.kernel,
                                         initrd=opts.initrd,
                                         iso=opts.iso,
                                         graphics=opts.graphics_port,
                                         vcpus=opts.vcpus,
                                         extra=opts.extra,
                                         keymap=opts.keymap,
                                         bus=opts.bus,
                                         disk_format=opts.disk_format,
                                         storage_pool=opts.storage_pool,
                                         storage_volume=opts.storage_volume,
                                         ) is True:
                    raise KssCommandException('Failed to create guest. - dom=%s' % (opts.name))

            except Exception, e:
                self.logger.error('Failed to create guest. - dom=%s - detail %s' % (opts.name, str(e.args)))
                print >>sys.stderr, _('Failed to create guest. - dom=%s - detail %s') % (opts.name, str(e.args))
                raise e

            self.up_progress(40)
            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if not (opts.name in active_guests or opts.name in inactive_guests):
                raise KssCommandException('Guest OS is not recognized. - dom=%s' % (opts.name))

            self.logger.info('Created guest. - dom=%s' % (opts.name))
            print >>sys.stdout, 'Created guest. - dom=%s' % opts.name
            return True

        finally:
            conn.close()

if __name__ == "__main__":
    target = CreateGuest()
    sys.exit(target.run())
