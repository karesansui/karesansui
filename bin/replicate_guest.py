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
すべてのディスクがfile形式のみ実行可能です。
</comment-ja>
<comment-en>
The only executable file format all disks.
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
    from karesansui.lib.utils import load_locale, is_uuid
    from karesansui.lib.const import PORT_MIN_NUMBER, PORT_MAX_NUMBER
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-s', '--src-name', dest='src_name', help=_('Source domain name'))
    optp.add_option('-d', '--dest-name', dest='name', help=_('Destination domain name'))
    optp.add_option('-v', '--vnc-port', dest='vnc_port', help=_('VNC port number'), default=None)
    optp.add_option('-u', '--uuid', dest='uuid', help=_('UUID'), default=None)
    optp.add_option('-a', '--mac', dest='mac', help=_('MAC address'), default=None)
    optp.add_option('-p', '--pool', dest='pool', help=_('Destination storage pool'))
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-d or --dest-name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-d or --dest-name')

    if opts.src_name:
        if reg.search(opts.src_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-s or --src-name', opts.src_name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-s or --src-name')

    if opts.pool:
        if reg.search(opts.pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool', opts.pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --pool')

    if opts.vnc_port:
        reg = re.compile("^[0-9]{1,5}$")
        if not reg.match(opts.vnc_port):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-v or --vnc-port', opts.vnc_port))
        if int(opts.vnc_port) < PORT_MIN_NUMBER or PORT_MAX_NUMBER < int(opts.vnc_port):
            raise KssCommandOptException('ERROR: Illigal port number. port=%s' % (opts.vnc_port))

    if opts.mac:
        reg = re.compile("^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")
        if not reg.match(opts.mac):
            raise KssCommandOptException('ERROR: Illigal MAC address. mac=%s' % (opts.mac))

    if opts.uuid:
        if not is_uuid(opts.uuid):
            raise KssCommandOptException('ERROR: Illigal UUID. uuid=%s' % (opts.uuid))

class ReplicateGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            # dest storage pool
            dest_target_path = conn.get_storage_pool_targetpath(opts.pool)
            if not dest_target_path:
                raise KssCommandException(
                    "Could not get the target path of the storage pool. - path=%s" % dest_target_path)

            self.dest_disk = "%s/%s/images/%s.img" \
                             % (dest_target_path, opts.name,opts.name,)

            # source storage pool
            src_pool = conn.get_storage_pool_name_bydomain(opts.src_name, "os")
            if not src_pool:
                raise KssCommandException("Source storage pool is not found.")
            src_pool_type = conn.get_storage_pool_type(src_pool)
            if src_pool_type == 'dir':
                raise KssCommandException(
                    "Storage pool type 'dir' is not. - type=%s" % src_pool_type)

            src_target_path = conn.get_storage_pool_targetpath(src_pool[0])
            self.src_disk  = "%s/%s/images/%s.img" \
                             % (src_target_path, opts.src_name,opts.src_name,)

            if os.path.isfile(self.src_disk) is False:
                raise KssCommandException(
                    'source disk image is not found. - src=%s' % (self.src_disk))

            if os.path.isfile(self.dest_disk) is True:
                raise KssCommandException(
                    'destination disk image already exists. - dest=%s' % (self.dest_disk))

            self.up_progress(10)

            active_storage_pools = conn.list_active_storage_pool()
            self.up_progress(10)
            if not (opts.pool in active_storage_pools):
                raise KssCommandException('Storage pool does not exist. - pool=%s'
                                          % (opts.pool))

            try:
                active_guests = conn.list_active_guest()
                inactive_guests = conn.list_inactive_guest()
                # source guestos
                if not (opts.src_name in active_guests or opts.src_name in inactive_guests):
                    raise KssCommandException(
                        "Unable to get the source guest OS. - src_name=%s" % opts.src_name)

                if (opts.name in active_guests or opts.name in inactive_guests):
                    raise KssCommandException(
                        "Destination Guest OS is already there. - dest_name=%s" % opts.name)

                self.up_progress(10)

                conn.replicate_guest(opts.name,
                                     opts.src_name,
                                     opts.pool,
                                     opts.mac,
                                     opts.uuid,
                                     opts.vnc_port)
                self.up_progress(40)
            except:
                self.logger.error('Failed to replicate guest. - src=%s dom=%s' % (opts.src_name,opts.name))
                raise
        finally:
            conn.close()

        conn1 = KaresansuiVirtConnection(readonly=False)
        try:
            self.up_progress(10)
            active_guests = conn1.list_active_guest()
            inactive_guests = conn1.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:
                self.logger.info('Replicated guest. - src=%s dom=%s' % (opts.src_name,opts.name))
                print >>sys.stdout, _('Replicated guest. - src=%s dom=%s') % (opts.src_name,opts.name)
                return True
            else:
                raise KssCommandException(
                    'Replicate guest not found. - src=%s dom=%s' % (opts.src_name,opts.name))
        finally:
            conn1.close()

        return True

    """
    def sigusr1_handler(self, signum, frame):
        if os.path.exists(self.src_disk) and os.path.exists(self.dest_disk):
            s_size = os.path.getsize(self.src_disk)
            d_size = os.path.getsize(self.dest_disk)
            print int(d_size*100/s_size)
    """
    """
    def sigint_handler(self, signum, frame):
        if os.path.exists(self.dest_disk):
            os.unlink(self.dest_disk)
        self.logger.error('Aborted by user request.')
        print >> sys.stderr, _("Aborted by user request.")
        raise ""
    """

if __name__ == "__main__":
    target = ReplicateGuest()
    #signal.signal(signal.SIGUSR1, target.sigusr1_handler)
    #signal.signal(signal.SIGINT,  target.sigint_handler)
    sys.exit(target.run())
