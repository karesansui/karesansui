#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
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
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, KaresansuiVirtException
    from karesansui.lib.const import NETWORK_IFCONFIG_COMMAND, NETWORK_BRCTL_COMMAND
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Network name'))
    optp.add_option('-c', '--cidr', dest='cidr', help=_('Bridge IP address'), default=None)
    optp.add_option('-s', '--dhcp-start', dest='dhcp_start', help=_('DHCP start IP address'), default=None)
    optp.add_option('-e', '--dhcp-end', dest='dhcp_end', help=_('DHCP end IP address'), default=None)
    optp.add_option('-f', '--forward-dev', dest='forward_dev', help=_('Forward device'), default=None)
    optp.add_option('-m', '--forward-mode', dest='forward_mode', help=_('Forward mode'), default=None)
    optp.add_option('-b', '--bridge-name', dest='bridge_name', help=_('Bridge name'), default=None)
    optp.add_option('-a', '--autostart', dest='autostart', help=_('Autostart'), default="yes")
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if not (opts.cidr or opts.dhcp_start or opts.dhcp_end or opts.forward_dev or opts.forward_mode or opts.bridge_name):
        raise KssCommandOptException('ERROR: At least one option should be specified.')

class UpdateNetwork(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            forward = {"dev": opts.forward_dev,
                       "mode": opts.forward_mode,
                       }
            bridge  = opts.bridge_name

            if opts.autostart == "yes":
                autostart = True
            else:
                autostart = False

            self.up_progress(20)
            try:
                conn.update_network(opts.name, opts.cidr, opts.dhcp_start, opts.dhcp_end, forward, bridge, autostart=autostart)
            except:
                self.logger.error('Failed to update network. - net=%s' % (opts.name))
                raise

            # The network should be active now.
            # If not, we're going to start it up.
            active_networks = conn.list_active_network()
            if not (opts.name in active_networks):
                try:
                    conn.start_network(opts.name)
                except KaresansuiVirtException, e:
                    # try to bring down existing bridge
                    kvn = conn.search_kvn_networks(opts.name)[0]
                    try:
                        bridge_name = kvn.get_info()['bridge']['name']
                    except KeyError:
                        pass

                    ret, res = execute_command([NETWORK_IFCONFIG_COMMAND, bridge_name, 'down'])
                    ret, res = execute_command([NETWORK_BRCTL_COMMAND, 'delbr', bridge_name])

                    # try again
                    conn.start_network(opts.name)
                    self.up_progress(10)

            self.up_progress(10)
            active_networks = conn.list_active_network()
            if not (opts.name in active_networks):
                raise KssCommandException('Updated network but it\'s dead. - net=%s' % (opts.name))

            self.logger.info('Updated network. - net=%s' % (opts.name))
            print >>sys.stdout, _('Updated network. - net=%s') % (opts.name)
            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = UpdateNetwork()
    sys.exit(target.run())
