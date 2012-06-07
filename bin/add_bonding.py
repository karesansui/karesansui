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
import re
import logging
import fcntl
import string
import copy
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command, \
        get_ifconfig_info, is_writable, create_file, \
        copy_file,         move_file,   get_bridge_info, \
        comma_split
    from karesansui.lib.dict_op import DictOp
    from karesansui.lib.parser.ifcfg import ifcfgParser
    from karesansui.lib.parser.modprobe_conf import modprobe_confParser
    from karesansui.lib.const import BONDING_MODE, BONDING_CONFIG_MII_DEFAULT, \
        VENDOR_DATA_BONDING_EVACUATION_DIR, NETWORK_IFCFG_DIR, NETWORK_COMMAND, \
        NETWORK_IFDOWN_COMMAND,             NETWORK_BRCTL_COMMAND

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-d', '--dev', dest='dev', help=_('Bonding Target Device Name'), default=None)
    optp.add_option('-m', '--mode', dest='mode', help=_('Bonding Mode'), default="1")
    optp.add_option('-p', '--primary', dest='primary', help=_('Primary Device Name'), default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9,]")

    if opts.dev:
        if reg.search(opts.dev):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-d or --dev', opts.dev))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-d or --dev')

    if opts.primary:
        if reg.search(opts.primary):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --primary', opts.primary))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --primary')

    if opts.mode not in BONDING_MODE:
        raise KssCommandOptException('ERROR: Unknown bonding mode "%s".' % opts.mode)

class AddBonding(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        dev_list = comma_split(opts.dev)
        if len(dev_list) < 2:
            # TRANSLATORS:
            #    bondingするためのdeviceが少ないです
            raise KssCommandOptException('ERROR: Small device for bonding. - dev=%s' % (opts.dev))

        interface_list = get_ifconfig_info()
        for dev in dev_list:
            if dev not in interface_list:
                raise KssCommandOptException('ERROR: Bonding target device not found. - dev=%s' % (dev))

        if opts.primary not in dev_list:
            raise KssCommandOptException('ERROR: Primary device not found in bonding device. - primary=%s dev=%s' % (opts.primary, opts.dev))

        exist_bond_max_num = -1
        exist_bond_list = get_ifconfig_info("regex:^bond")
        for bond_name in exist_bond_list.keys():
            try:
                num = int(bond_name.replace("bond",""))
            except ValueError:
                continue

            if exist_bond_max_num < num:
                exist_bond_max_num = num

        self.up_progress(10)
        physical_bond_name = "bond%s" % (exist_bond_max_num + 1)
        bridge_bond_name = "bondbr%s" % (exist_bond_max_num + 1)
        bond_options = '"mode=%s primary=%s miimon=%s"' % (opts.mode, opts.primary, BONDING_CONFIG_MII_DEFAULT)
        self.up_progress(10)

        dop = DictOp()
        ifcfg_parser = ifcfgParser()
        modprobe_parser = modprobe_confParser()

        dop.addconf("ifcfg", ifcfg_parser.read_conf())
        if dop.getconf("ifcfg") == {}:
            raise KssCommandException('Failure read network config file.')

        dop.addconf("modprobe_conf", modprobe_parser.read_conf())
        if dop.getconf("modprobe_conf") == {}:
            raise KssCommandException('Failure read modprobe config file.')

        self.up_progress(10)
        eth_conf_copykey = ["HWADDR",
                            "BOOTPROTO",
                            "ONBOOT",
                            "USERCTL",
                            ]
        bond_conf_nocopykey = ["TYPE",
                               "HWADDR",
                               "MACADDR",
                               "ETHTOOL_OPTS",
                               "ESSID",
                               "CHANNEL",
                               ]

        self.up_progress(10)
        for dev in dev_list:
            conf = dop.get("ifcfg", dev)
            if dev == opts.primary:
                primary_conf = copy.deepcopy(conf)

            dop.unset("ifcfg", dev)
            dop.set("ifcfg", [dev, "DEVICE"], conf["DEVICE"]["value"])
            for key in eth_conf_copykey:
                if key in conf:
                    dop.set("ifcfg", [dev, key], conf[key]["value"])
            dop.set("ifcfg", [dev, "MASTER"], physical_bond_name)
            dop.set("ifcfg", [dev, "SLAVE"], "yes")
            dop.set("ifcfg", [dev, "BOOTPROTO"], "none")

            if dop.get("ifcfg", "p%s" % (dev)):
                hwaddr = dop.get("ifcfg", ["p%s" % (dev), "HWADDR"])
                if hwaddr:
                    dop.set("ifcfg", [dev, "HWADDR"], hwaddr)
                dop.unset("ifcfg", "p%s" % (dev))

        for key in bond_conf_nocopykey:
            if key in primary_conf:
                del primary_conf[key]

        dop.set("ifcfg", bridge_bond_name, primary_conf)
        dop.set("ifcfg", [bridge_bond_name, "DEVICE"], bridge_bond_name)
        dop.set("ifcfg", [bridge_bond_name, "TYPE"], "Bridge")

        dop.set("ifcfg", [physical_bond_name, "DEVICE"], physical_bond_name)
        dop.set("ifcfg", [physical_bond_name, "BRIDGE"], bridge_bond_name)
        dop.set("ifcfg", [physical_bond_name, "BOOTPROTO"], "none")
        dop.set("ifcfg", [physical_bond_name, "ONBOOT"], dop.get("ifcfg", [bridge_bond_name, "ONBOOT"]))
        dop.set("ifcfg", [physical_bond_name, "BONDING_OPTS"], bond_options)

        self.up_progress(10)
        dop.set("modprobe_conf", ["alias", physical_bond_name], "bonding")

        for dev in dev_list:
            if os.path.isfile("%s/ifcfg-%s" % (NETWORK_IFCFG_DIR, dev)):
                copy_file("%s/ifcfg-%s" % (NETWORK_IFCFG_DIR, dev), VENDOR_DATA_BONDING_EVACUATION_DIR)
            if os.path.isfile("%s/ifcfg-p%s" % (NETWORK_IFCFG_DIR, dev)):
                move_file("%s/ifcfg-p%s" % (NETWORK_IFCFG_DIR, dev), VENDOR_DATA_BONDING_EVACUATION_DIR)

        if ifcfg_parser.write_conf(dop.getconf("ifcfg")) is False:
            raise KssCommandException('Failure write network config file.')

        if modprobe_parser.write_conf(dop.getconf("modprobe_conf")) is False:
            raise KssCommandException('Failure write modprobe config file.')

        self.up_progress(10)
        #
        # Delete bridge device
        #
        bridge_list = get_bridge_info()
        for dev in dev_list:
            if dev in bridge_list:
                ifdown_cmd = (NETWORK_IFDOWN_COMMAND,
                              dev,
                              )
                (ifdown_rc, ifdown_res) = execute_command(ifdown_cmd)
                if ifdown_rc != 0:
                    raise KssCommandException('Failure stop interface. interface:%s' % (dev))

                for brif in bridge_list[dev]:
                    brctl_delif_cmd = (NETWORK_BRCTL_COMMAND,
                                       "delif",
                                       dev,
                                       brif,
                                       )
                    (brctl_rc, brctl_res) = execute_command(brctl_delif_cmd)
                    if brctl_rc != 0:
                        raise KssCommandException('Failure delete bridge port. bridge:%s port:%s' % (dev, brif))

                brctl_delbr_cmd = (NETWORK_BRCTL_COMMAND,
                                   "delbr",
                                   dev,
                                   )
                (brctl_rc, brctl_res) = execute_command(brctl_delbr_cmd)
                if brctl_rc != 0:
                    raise KssCommandException('Failure delete bridge. bridge:%s' % (dev, brif))

        self.up_progress(10)
        #
        # Restart network
        #
        network_restart_cmd = (NETWORK_COMMAND,
                               "restart",
                               )
        (net_rc, net_res) = execute_command(network_restart_cmd)
        if net_rc != 0:
            raise KssCommandException('Failure restart network.')

        self.logger.info("Created bonding device. - dev=%s bond=%s" % (opts.dev, bridge_bond_name))
        print >>sys.stdout, _("Created bonding device. - dev=%s bond=%s" % (opts.dev, bridge_bond_name))

        return True

if __name__ == "__main__":
    target = AddBonding()
    sys.exit(target.run())
