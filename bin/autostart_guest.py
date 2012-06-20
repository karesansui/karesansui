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
                                         KaresansuiVirtConnectionAuth
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
    optp.add_option('-e', '--enable', dest='enable', action="store_true", help=_('Enable autostart'))
    optp.add_option('-d', '--disable', dest='disable', action="store_true", help=_('Disable autostart'))
    optp.add_option('-c', '--connection', dest='uri', help=_('Connection URI'), default=None)
    optp.add_option('-w', '--passwd-file', dest='passwd_file', help=_('Password File for URI Connection'), default=None)
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.enable is None and opts.disable is None:
        raise KssCommandOptException('ERROR: either %s options must be specified.' % '--enable or --disable')

    if opts.enable is not None and opts.disable is not None:
        raise KssCommandOptException('ERROR: %s options are conflicted.' % '--enable and --disable')

    if opts.passwd_file is not None and not os.path.exists(opts.passwd_file):
        raise KssCommandOptException('ERROR: %s is not found.' % opts.passwd_file)

    if opts.uri is not None:
        if uri_split(opts.uri)["scheme"] is None:
            raise KssCommandOptException('ERROR: uri %s is invalid.' % opts.uri)

class AutostartGuest(KssCommand):

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

            flag = None
            if opts.enable:
                flag = True
            if opts.disable:
                flag = False
            self.up_progress(10)
            ret = conn.autostart_guest(flag)
            self.up_progress(40)

        except Exception, e:

            if flag is True:
                self.logger.error('Failed to configure a domain to be automatically started at boot. - dom=%s' % (opts.name))
                print >>sys.stderr, _('Failed to configure a domain to be automatically started at boot. - dom=%s') % (opts.name)
            else:
                self.logger.error('Failed to configure a domain not to be automatically started at boot. - dom=%s' % (opts.name))
                print >>sys.stderr, _('Failed to configure a domain not to be automatically started at boot. - dom=%s') % (opts.name)

            raise e

        finally:
            if 'conn' in locals():
                conn.close()

        if ret is False:
            raise KssCommandException('Failed to set autostart flag. - dom=%s flag=%s' \
                              % (opts.name,flag))

        self.logger.info('Set autostart flag. - dom=%s flag=%s' \
                         % (opts.name,flag))
        print >>sys.stdout, _('Set autostart flag. - dom=%s flag=%s') \
              % (opts.name,flag)
        return True

if __name__ == "__main__":
    target = AutostartGuest()
    sys.exit(target.run())
