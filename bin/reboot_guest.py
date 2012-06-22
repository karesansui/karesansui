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
import fcntl
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, \
                                         KaresansuiVirtConnectionAuth, \
                                         VIR_DOMAIN_SHUTOFF, VIR_DOMAIN_SHUTDOWN
    from karesansui.lib.utils import load_locale
    from karesansui.lib.utils import uri_split, uri_join

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-c', '--connection', dest='uri', help=_('Connection URI'), default=None)
    optp.add_option('-w', '--passwd-file', dest='passwd_file', help=_('Password File for URI Connection'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: -n or --name option is required.')

    if opts.passwd_file is not None and not os.path.exists(opts.passwd_file):
        raise KssCommandOptException('ERROR: %s is not found.' % opts.passwd_file)

    if opts.uri is not None:
        if uri_split(opts.uri)["scheme"] is None:
            raise KssCommandOptException('ERROR: uri %s is invalid.' % opts.uri)

class RebootGuest(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        passwd = None
        if opts.passwd_file is not None and os.path.exists(opts.passwd_file):
            try:
                fp = open(opts.passwd_file, "r")
                try:
                    self.up_progress(10)
                    fcntl.lockf(fp.fileno(), fcntl.LOCK_SH)
                    try:
                        passwd = fp.readline().strip("\n")
                    finally:
                        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
                    self.up_progress(10)
                finally:
                    fp.close()

            except Exception, e:
                self.logger.error('Failed to read.- dom=%s passwd_file=%s' \
                      % (opts.name,opts.passwd_file))
                print >>sys.stderr,_('Failed to read.- dom=%s passwd_file=%s') \
                      % (opts.name,opts.passwd_file)
                raise e

            os.remove(opts.passwd_file)

        try:
            if passwd is None:
                if opts.uri is None:
                    conn = KaresansuiVirtConnection(readonly=False)
                else:
                    uri = uri_join(uri_split(opts.uri), without_auth=True)
                    conn = KaresansuiVirtConnection(uri, readonly=False)

            else:
                if opts.uri is None:
                    conn = KaresansuiVirtConnectionAuth(creds=passwd,readonly=False)
                else:
                    uri = uri_join(uri_split(opts.uri), without_auth=True)
                    conn = KaresansuiVirtConnectionAuth(uri,creds=passwd,readonly=False)

            conn.set_domain_name(opts.name)

            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:
                try:
                    self.up_progress(10)
                    conn.reboot_guest()
                    self.up_progress(30)
                except Exception, e:
                    self.logger.error('Failed to reboot guest. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to reboot guest. - dom=%s') % (opts.name)
                    raise e

                self.up_progress(10)
                status = conn.guest.status()
                self.up_progress(10)
                if status != VIR_DOMAIN_SHUTOFF and status != VIR_DOMAIN_SHUTDOWN:
                    self.logger.info('Succeeded to reboot guest. - dom=%s' % (opts.name))
                    print >>sys.stdout, _('Succeeded to reboot guest. - dom=%s') % (opts.name)

            else:
                raise KssCommandException(
                    'guest not found. - dom=%s' % (opts.name))

            return True

        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    target = RebootGuest()
    sys.exit(target.run())
