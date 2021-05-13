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
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale

except ImportError as e:
    print("[Error] some packages not found. - %s" % e, file=sys.stderr)
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Network name'))
    optp.add_option('-c', '--cidr', dest='cidr', help=_('Bridge IP address'), default=None)
    optp.add_option('-s', '--dhcp-start', dest='dhcp_start', help=_('DHCP start address'), default=None)
    optp.add_option('-e', '--dhcp-end', dest='dhcp_end', help=_('DHCP end address'), default=None)
    optp.add_option('-f', '--forward-dev', dest='forward_dev', help=_('Forward device'), default=None)
    optp.add_option('-m', '--forward-mode', dest='forward_mode', help=_('Forward mode'), default=None)
    optp.add_option('-b', '--bridge-name', dest='bridge_name', help=_('Bridge name'), default=None)
    optp.add_option('-a', '--autostart', dest='autostart', help=_('Autostart'), default="yes")
    return optp.parse_args()

def chkopts(opts):
    if opts.name is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.cidr is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-c or --cidr')

    if opts.dhcp_start is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-s or --dhcp-start')

    if opts.dhcp_end is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-e or --dhcp-end')

    if opts.bridge_name is None:
        raise KssCommandOptException('ERROR: %s option is required.' % '-b or --bridge_name')

class CreateNetwork(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            forward = {"dev" : opts.forward_dev,
                       "mode": opts.forward_mode,
                       }
            bridge  = opts.bridge_name

            if opts.autostart == "yes":
                autostart = True
            else:
                autostart = False

            active_networks = conn.list_active_network()
            inactive_networks = conn.list_inactive_network()

            self.up_progress(10)
            if opts.name in active_networks or opts.name in inactive_networks:
                raise KssCommandException('network already exists. - net=%s' % (opts.name))

            self.up_progress(10)
            try:
                conn.create_network(opts.name, opts.cidr, opts.dhcp_start, opts.dhcp_end, forward, bridge, autostart=autostart)
            except:
                raise KssCommandException('Failed to create network. - net=%s' % (opts.name))

            self.up_progress(40)
            active_networks = conn.list_active_network()
            inactive_networks = conn.list_inactive_network()
            if not (opts.name in active_networks or opts.name in inactive_networks):
                raise KssCommandException('Failed to create the network. - net=%s' % (opts.name))

            self.logger.info('Created network. - net=%s' % (opts.name))
            print(_('Created network. - net=%s') % (opts.name), file=sys.stdout)
            self.up_progress(10)

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = CreateNetwork()
    sys.exit(target.run())
