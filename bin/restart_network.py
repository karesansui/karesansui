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
    from karesansui.lib.utils import execute_command
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Network name'))
    optp.add_option('-f', '--force', dest='force', action="store_true", help=_('Do everything to bring up network'))
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

class RestartNetwork(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            active_networks = conn.list_active_network()
            inactive_networks = conn.list_inactive_network()
            if not (opts.name in active_networks or opts.name in inactive_networks):
                raise KssCommandException('Could not find the specified network. - net=%s' % (opts.name))

            self.up_progress(10)
            try:
                conn.stop_network(opts.name)
            except KaresansuiVirtException, e:
                if opt.force is not True:
                    raise KssCommandException('Could not stop the specified network. - net=%s' % (opts.name))

            self.up_progress(20)

            try:
                conn.start_network(opts.name)
            except KaresansuiVirtException, e:
                if opts.force is not True:
                    raise KssCommandException('Could not start the specified network. - net=%s' % (opts.name))

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
            if not (opts.name in conn.list_active_network()):
                raise KssCommandException('Failed to start network. - net=%s' % (opts.name))

            self.logger.info('Restarted network. - net=%s' % (opts.name))
            print >>sys.stdout, _('Restarted network. - net=%s') % (opts.name)

            return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = RestartNetwork()
    sys.exit(target.run())
