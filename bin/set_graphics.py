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
import fcntl
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, generate_phrase
    from karesansui.lib.const import DEFAULT_KEYMAP

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-P', '--passwd', dest='passwd', help=_('Graphics Password'), default=None)
    optp.add_option('-w', '--passwd-file', dest='passwd_file', help=_('Graphics Password File'), default=None)
    optp.add_option('-W', '--random-passwd', dest='random_passwd', action="store_true", help=_('Set random Graphics password'))
    optp.add_option('-p', '--port', dest='port', help=_('Graphics Port Number'), default=None)
    optp.add_option('-l', '--listen', dest='listen', help=_('Graphics Listen Address'), default='0.0.0.0')
    optp.add_option('-k', '--keymap', dest='keymap', help=_('Graphics Keyboard Map'), default=DEFAULT_KEYMAP)
    optp.add_option('-t', '--type', dest='type', help=_('Graphics Service Type'), default='vnc')
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')
    if opts.passwd_file is not None and not os.path.exists(opts.passwd_file):
        raise KssCommandOptException('ERROR: %s is not found.' % opts.passwd_file)
    if opts.passwd != None and opts.passwd_file != None and opts.random_passwd != None:
        raise KssCommandOptException('ERROR: %s options are conflicted.' % '--passwd, --passwd-file and --random-passwd')

class SetGraphics(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            conn.set_domain_name(opts.name)

            passwd = None
            if opts.passwd is not None:
                passwd = opts.passwd
            elif opts.passwd_file is not None and os.path.exists(opts.passwd_file):
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
                    self.logger.error('Failed to read file. - dom=%s passwd_file=%s' \
                                      % (opts.name,opts.passwd_file))
                    print >>sys.stderr, _('Failed to read file. - dom=%s passwd_file=%s') \
                          % (opts.name,opts.passwd_file)
                    raise e

                os.remove(opts.passwd_file)
                self.up_progress(10)

            elif opts.random_passwd and opts.random_passwd is not None:
                passwd = generate_phrase(8,'23456789abcdefghijkmnpqrstuvwxyz')

            active_guests = conn.list_active_guest()
            inactive_guests = conn.list_inactive_guest()
            if opts.name in active_guests or opts.name in inactive_guests:

                try:
                    self.up_progress(10)
                    conn.guest.set_graphics(port=opts.port,
                                       listen=opts.listen,
                                       passwd=passwd,
                                       keymap=opts.keymap,
                                       type=opts.type)
                    self.up_progress(20)
                    info = conn.guest.get_graphics_info()
                    self.up_progress(10)

                    self.logger.info('Set graphics. - dom=%s type=%s port=%s listen=%s passwd=%s keymap=%s' \
                                     % (opts.name, info['setting']['type'], info['setting']['port'], info['setting']['listen'],"xxxxxx", info['setting']['keymap']))
                    print >>sys.stdout, _('Set graphics. - dom=%s type=%s port=%s listen=%s passwd=%s keymap=%s') \
                          % (opts.name, info['setting']['type'], info['setting']['port'], info['setting']['listen'],"xxxxxx", info['setting']['keymap'])

                except Exception, e:
                    self.logger.error('Failed to set graphics. - dom=%s' % (opts.name))
                    print >>sys.stderr, _('Failed to set graphics. - dom=%s') % (opts.name)
                    raise e

            else:
                raise KssCommandException('guest not found. - dom=%s' % (opts.name))

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = SetGraphics()
    sys.exit(target.run())
