#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import os
import sys
import logging
import fcntl
import string
import copy
import re
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command, get_ifconfig_info, \
        is_writable, create_file, move_file, remove_file, get_bridge_info
    from karesansui.lib.dict_op import DictOp
    from karesansui.lib.parser.ifcfg import ifcfgParser
    from karesansui.lib.parser.modprobe_conf import modprobe_confParser
    from karesansui.lib.const import BONDING_MODE, BONDING_CONFIG_MII_DEFAULT, \
        VENDOR_DATA_BONDING_EVACUATION_DIR, NETWORK_IFCFG_DIR, NETWORK_COMMAND, \
        SYSTEM_COMMAND_REMOVE_MODULE, NETWORK_IFDOWN_COMMAND, NETWORK_BRCTL_COMMAND

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-d', '--dev', dest='dev', help=_('Bonding target device name'), default=None)
    optp.add_option('-s', '--succession', dest='succession', action="store_true", help=_('Succeed IP address settings of the primary device.'), default=False)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9]")

    if opts.dev:
        if reg.search(opts.dev):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-d or --dev', opts.dev))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-d or --dev')

class DeleteBonding(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        exist_bond_list = get_ifconfig_info("regex:^bond")
        if opts.dev not in exist_bond_list:
            raise KssCommandOptException('Target bonding device not found. target=%s' % opts.dev)

        self.up_progress(10)
        dop = DictOp()
        ifcfg_parser = ifcfgParser()
        dop.addconf("ifcfg", ifcfg_parser.read_conf())
        if dop.getconf("ifcfg") == {}:
            raise KssCommandException('Failure read network config file.')

        if dop.get("ifcfg", opts.dev) is False:
            raise KssCommandException('Target device ifcfg file not found.')

        self.up_progress(10)
        restore_dev_list = []
        for dev in dop.getconf("ifcfg").keys():
            if dop.get("ifcfg", [dev, "MASTER"]) == opts.dev:
                restore_dev_list.append(dev)

        self.up_progress(10)
        if opts.succession is True:
            bond_bridge = dop.get("ifcfg", [opts.dev, "BRIDGE"])
            bond_dev = opts.dev
            if bond_bridge:
                bond_dev = bond_bridge

            ipaddr = dop.get("ifcfg",  [bond_dev, "IPADDR"])
            netmask = dop.get("ifcfg", [bond_dev, "NETMASK"])
            gateway = dop.get("ifcfg", [bond_dev, "GATEWAY"])
            bonding_opts = dop.get("ifcfg", [opts.dev, "BONDING_OPTS"])
            bonding_opts = bonding_opts.strip('"')
            primary_dev = None
            for combination in bonding_opts.split(" "):
                if re.match("primary", combination):
                    (key,val) = combination.split("=")
                    val = val.strip()
                    primary_dev = val

        self.up_progress(10)
        for restore_dev in restore_dev_list:
            if move_file("%s/ifcfg-%s" % (VENDOR_DATA_BONDING_EVACUATION_DIR, restore_dev), NETWORK_IFCFG_DIR) is False:
                raise KssCommandException('Failure restore ifcfg file.')
            if os.path.isfile("%s/ifcfg-p%s" % (VENDOR_DATA_BONDING_EVACUATION_DIR, restore_dev)):
                if move_file("%s/ifcfg-p%s" % (VENDOR_DATA_BONDING_EVACUATION_DIR, restore_dev), NETWORK_IFCFG_DIR) is False:
                    raise KssCommandException('Failure restore ifcfg file.')

        self.up_progress(10)
        if opts.succession is True and primary_dev is not None:
            dop = DictOp()
            ifcfg_parser = ifcfgParser()
            dop.addconf("ifcfg", ifcfg_parser.read_conf())
            if dop.getconf("ifcfg") == {}:
                raise KssCommandException('Failure read network config file.')

            if ipaddr:
                dop.set("ifcfg", [primary_dev, "IPADDR"],  ipaddr)
            if netmask:
                dop.set("ifcfg", [primary_dev, "NETMASK"], netmask)
            if gateway:
                dop.set("ifcfg", [primary_dev, "GATEWAY"], gateway)

            if ifcfg_parser.write_conf(dop.getconf("ifcfg")) is False:
                raise KssCommandException('Failure write network config file.')

        self.up_progress(10)
        remove_file("%s/ifcfg-%s" % (NETWORK_IFCFG_DIR, opts.dev))

        self.up_progress(10)
        dop = DictOp()
        modprobe_parser = modprobe_confParser()
        dop.addconf("modprobe_conf", modprobe_parser.read_conf())
        if dop.getconf("modprobe_conf") == {}:
            raise KssCommandException('Failure read modprobe config file.')

        dop.unset("modprobe_conf", ["alias", opts.dev])

        if modprobe_parser.write_conf(dop.getconf("modprobe_conf")) is False:
            raise KssCommandException('Failure write modprobe config file.')

        self.up_progress(10)

        #
        # Delete bridge device
        #
        bridge_list = get_bridge_info()
        bond_bridge = None

        for bridge in bridge_list:
            if opts.dev in bridge_list[bridge]:
                bond_bridge = bridge

        if bond_bridge:
            ifdown_cmd = (NETWORK_IFDOWN_COMMAND,
                          bond_bridge,
                          )
            (ifdown_rc, ifdown_res) = execute_command(ifdown_cmd)
            if ifdown_rc != 0:
                raise KssCommandException('Failure stop interface. interface:%s' % (dev))

            for brif in bridge_list[bond_bridge]:
                brctl_delif_cmd = (NETWORK_BRCTL_COMMAND,
                                   "delif",
                                   bond_bridge,
                                   brif,
                                   )
                (brctl_rc, brctl_res) = execute_command(brctl_delif_cmd)
                if brctl_rc != 0:
                    raise KssCommandException('Failure delete bridge port. bridge:%s port:%s' % (dev, brif))

            brctl_delbr_cmd = (NETWORK_BRCTL_COMMAND,
                               "delbr",
                               bond_bridge,
                               )
            (brctl_rc, brctl_res) = execute_command(brctl_delbr_cmd)
            if brctl_rc != 0:
                raise KssCommandException('Failure delete bridge. bridge:%s' % (dev, brif))

            remove_file("%s/ifcfg-%s" % (NETWORK_IFCFG_DIR, bond_bridge))

        #
        # Unload bonding module
        #
        remove_bonding_cmd = (SYSTEM_COMMAND_REMOVE_MODULE,
                              "bonding",
                              )
        (rmmod_rc, rmmod_res) = execute_command(remove_bonding_cmd)
        if rmmod_rc != 0:
            raise KssCommandException('Failure remove bonding module.')

        #
        # Restart network
        #
        network_restart_cmd = (NETWORK_COMMAND,
                               "restart",
                               )
        (net_rc, net_res) = execute_command(network_restart_cmd)
        if net_rc != 0:
            raise KssCommandException('Failure restart network.')

        self.logger.info("Deleted bonding device. - bond=%s dev=%s" % (opts.dev, ','.join(restore_dev_list)))
        print >>sys.stdout, _("Deleted bonding device. - bond=%s dev=%s" % (opts.dev, ','.join(restore_dev_list)))

        return True

if __name__ == "__main__":
    target = DeleteBonding()
    sys.exit(target.run())
