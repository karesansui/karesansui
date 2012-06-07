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
import traceback
from optparse import OptionParser
import shutil

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale
    from karesansui.db.access.machine import findby1uniquekey, deleteby1uniquekey
    from karesansui.db.access.machine2jobgroup import deleteby1machine
    from karesansui.lib.const import XEN_VIRT_CONFIG_DIR, KVM_VIRT_CONFIG_DIR, \
                    VIRT_XML_CONFIG_DIR

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-p', '--pool', dest='pool', help=_('Storage Pool Name'))
    optp.add_option('-v', '--volume', dest='volume', help=_('Storage Volume Name'))
    #optp.add_option('-f', '--force', dest='force', action="store_true", default=False, help=_('To remove the storage volume even more.'))

    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: -n or --name option is required.')

    if not opts.pool:
        raise KssCommandOptException('ERROR: -p or --pool option is required.')

class DeleteGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            uuid = conn.domname_to_uuid(opts.name)
            try: # physical
                conn.set_domain_name(opts.name)
                conn.delete_guest(opts.name, opts.pool, opts.volume)
                self.up_progress(20)
            except Exception, e:
                print >>sys.stderr, '[Warn] Failed to delete the guest OS physical. - dom=%s - detail : %s' \
                      % (opts.name, str(e.args))
                self.logger.warn('Failed to delete the guest OS physical. - dom=%s - detail : %s' \
                                 % (opts.name, str(e.args)))

            # Check the presence of residual files
            try:
                self.up_progress(10)
                # /etc
                config = ""
                hypervisor = conn.get_hypervisor_type()
                if hypervisor == "XEN":
                    config = "%s/%s" % (XEN_VIRT_CONFIG_DIR, opts.name,)
                elif hypervisor == "KVM" or hypervisor == "QEMU":
                    config = "%s/%s" % (KVM_VIRT_CONFIG_DIR, opts.name,)
                if os.path.isfile(config) is True:
                    os.remove(config)
                    self.logger.info("physical config remove. - path=%s" % config)

                self.up_progress(5)

                xml_config = '%s/%s.xml' % (VIRT_XML_CONFIG_DIR, opts.name)
                if os.path.isfile(xml_config) is True:
                    os.remove(xml_config)
                    self.logger.info("physical xml config remove. - path=%s" % xml_config)

                self.up_progress(5)

                self.logger.info('To remove the storage volume even more.')

                tmp_pool = conn.get_storage_pool_name_bydomain(opts.name, 'os')
                if tmp_pool:
                    domains_dir = conn.get_storage_pool_targetpath(tmp_pool[0])
                else:
                    domains_dir = conn.get_storage_pool_targetpath(opts.pool)

                disk_image = '%s/%s/images/%s.img' % (domains_dir, opts.name, opts.name,)
                if os.path.isfile(disk_image) is True or os.path.islink(disk_image) is True:
                    os.remove(disk_image)
                    self.logger.info("physical disk image remove. - path=%s" % disk_image)

                self.up_progress(5)
                if 0 < len(opts.name.split()): # double check
                    snapshot_dir = '%s/%s/snapshot' % (domains_dir, opts.name,)
                    if os.path.isdir(snapshot_dir) is True:

                        for root, dirs, files in os.walk(snapshot_dir):
                            for fname in files:
                                file_path = os.path.join(root, fname)
                                os.remove(file_path)
                                self.logger.info("physical snapshots file remove. - file=%s" % file_path)

                        os.removedirs(snapshot_dir)
                        self.logger.info("physical snapshots directory remove. - dir=%s" % snapshot_dir)

                self.up_progress(5)
                if 0 < len(opts.name.split()): # double check
                    disk_dir = '%s/%s/disk' % (domains_dir, opts.name,)
                    if os.path.isdir(disk_dir) is True:

                        for root, dirs, files in os.walk(disk_dir):
                            for fname in files:
                                file_path = os.path.join(root, fname)
                                os.remove(file_path)
                                self.logger.info("physical disk file remove. - file=%s" % file_path)

                        os.removedirs(disk_dir)
                        self.logger.info("physical disk directory remove. - dir=%s" % disk_dir)
                self.up_progress(5)

                # Delete GuestOS directory
                domain_dir = "%s/%s" % (domains_dir, opts.name)
                if os.path.isdir(domain_dir) is True:
                    shutil.rmtree(domain_dir)

                self.up_progress(5)

            except Exception, e:
                print >>sys.stderr, '[Warn] Failed to remove the residual file.. - dom=%s - detail : %s' \
                      % (opts.name, str(e.args))
                self.logger.warn('Failed to remove the residual file.. - dom=%s - detail : %s' \
                                 % (opts.name, str(e.args)))

            # database
            try:
                if uuid == '':
                    raise KssCommandException('UUID did not get that.')

                # rollback - machine
                self.up_progress(5)
                deleteby1uniquekey(self.kss_session, u"%s" % uuid)
                self.up_progress(5)
            except KssCommandException, e:
                print >>sys.stderr, '[Warn] Failed to delete the guest OS database. - dom=%s - detail : %s' \
                      % (opts.name, str(e.args))
                self.logger.warn('Failed to delete the guest OS database. - dom=%s - detail : %s' \
                                 % (opts.name, str(e.args)))

            self.logger.info('deleted guestos. - dom=%s' % opts.name)
            print >>sys.stdout, 'deleted guestos. - dom=%s' % opts.name
            return True

        finally:
            conn.close()

if __name__ == "__main__":
    target = DeleteGuest()
    sys.exit(target.run())
