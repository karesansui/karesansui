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
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale, get_pwd_info, get_grp_info
    from karesansui.lib.const import STORAGE_POOL_TYPE

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name',        dest='name',        help=_('Name'),                           default=None)
    optp.add_option('-t', '--type',        dest='type',        help=_('Pool Type (dir or iscsi or fs)'), default=None)
    optp.add_option('-p', '--target_path', dest='target_path', help=_('Target path (dir, fs)'),          default=None)
    #optp.add_option('-a', '--allocation',  dest='allocation',  help=_('Allocation'),                     default=0, type="int")
    #optp.add_option('-v', '--available',   dest='available',   help=_('Available'),                      default=0, type="int")
    #optp.add_option('-c', '--capacity',    dest='capacity',    help=_('Capacity'),                       default=0, type="int")
    optp.add_option('-b', '--host_name',   dest='host_name',   help=_('Host name (iscsi)'),              default=None)
    optp.add_option('-d', '--device_path', dest='device_path', help=_('Device path (iscsi, fs)'),        default=None)
    optp.add_option('-g', '--group',       dest='group',       help=_('Permission group'),               default=None)
    optp.add_option('-l', '--label',       dest='label',       help=_('Permission label'),               default=None)
    optp.add_option('-m', '--mode',        dest='mode',        help=_('Permission mode'),                default=None)
    optp.add_option('-o', '--owner',       dest='owner',       help=_('Permission owner'),               default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.type:
        if opts.type not in STORAGE_POOL_TYPE.values():
            raise KssCommandOptException('ERROR: Type is not available. type=%s' % opts.type)
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-t or --type')

    if opts.type == STORAGE_POOL_TYPE["TYPE_DIR"]:
        # type:dir
        if not opts.target_path:
            raise KssCommandOptException('ERROR: %s option is required.' % '-p or --target_path')

    elif opts.type == STORAGE_POOL_TYPE["TYPE_ISCSI"]:
        # type:iscsi
        if not opts.host_name:
            raise KssCommandOptException('ERROR: %s option is required.' % '-b or --host_name')
        if not opts.device_path:
            raise KssCommandOptException('ERROR: %s option is required.' % '-d or --device_path')

    elif opts.type == STORAGE_POOL_TYPE["TYPE_FS"]:
        # type:fs
        if not opts.target_path:
            raise KssCommandOptException('ERROR: %s option is required.' % '-p or --target_path')
        if not opts.device_path:
            raise KssCommandOptException('ERROR: %s option is required.' % '-d or --device_path')

    else:
        raise KssCommandOptException('ERROR: The type that does not exist. type=%s' % opts.type)

    if opts.label:
        if reg.search(opts.label):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-l or --label', opts.label))

    reg = re.compile("[^0-9]")
    if opts.owner:
        if reg.search(opts.owner):
            if opts.owner not in [user[0] for user in get_pwd_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. owner=%s' % (opts.owner))
        else:
            if int(opts.owner) not in [user[2] for user in get_pwd_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. owner=%s' % (opts.owner))

    if opts.group:
        if reg.search(opts.group):
            if opts.group not in [group[0] for group in get_grp_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. group=%s' % (opts.group))
        else:
            if int(opts.group) not in [group[2] for group in get_grp_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. group=%s' % (opts.group))

    reg = re.compile("^[0-9]{3,4}$")
    if opts.mode:
        if not reg.match(opts.mode):
            raise KssCommandOptException('ERROR: Illigal permission mode. mode=%s' % (opts.mode))

class CreateStoragePool(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)
        try:
            inactive_storage_pools = conn.list_inactive_storage_pool()
            active_storage_pools = conn.list_active_storage_pool()

            self.up_progress(10)

            if opts.name in active_storage_pools or opts.name in inactive_storage_pools:
                raise KssCommandException('Storage pool already exists. - pool=%s' % opts.name)

            try:
                if opts.type == STORAGE_POOL_TYPE["TYPE_DIR"]:
                    if conn.create_storage_pool(opts.name, opts.type,
                                                opts.target_path,
                                                #allocation=opts.allocation, available=opts.available,
                                                #capacity=opts.capacity,
                                                target_p_group=opts.group, target_p_label=opts.label,
                                                target_p_mode=opts.mode, target_p_owner=opts.owner,
                                                ) is False:
                        raise KssCommandException('Failed to create storage pools. - pool=%s' \
                                                  % opts.name)

                elif opts.type == STORAGE_POOL_TYPE["TYPE_ISCSI"]:
                    if conn.create_storage_pool(opts.name, opts.type,
                                                target_path="/dev/disk/by-path",
                                                source_h_name=opts.host_name,
                                                source_dev_path=opts.device_path,
                                                #allocation=opts.allocation, available=opts.available,
                                                #capacity=opts.capacity,
                                                target_p_group=opts.group, target_p_label=opts.label,
                                                target_p_mode=opts.mode, target_p_owner=opts.owner,
                                                ) is False:
                        raise KssCommandException('Failed to create storage pools. - pool=%s' \
                                                  % opts.name)

                elif opts.type == STORAGE_POOL_TYPE["TYPE_FS"]:
                    if conn.create_storage_pool(opts.name, opts.type,
                                                opts.target_path,
                                                source_dev_path=opts.device_path,
                                                #allocation=opts.allocation, available=opts.available,
                                                #capacity=opts.capacity,
                                                target_p_group=opts.group, target_p_label=opts.label,
                                                target_p_mode=opts.mode, target_p_owner=opts.owner,
                                                ) is False:
                        raise KssCommandException('Failed to create storage pools. - pool=%s' \
                                                  % opts.name)

                else:
                    raise KssCommandOptException('ERROR: The type that does not exist. type=%s' \
                                                 % opts.type)

                self.up_progress(20)
                # pool check
                inactive_storage_pools = conn.list_inactive_storage_pool()
                active_storage_pools = conn.list_active_storage_pool()

                if not (opts.name in active_storage_pools or opts.name in inactive_storage_pools):
                    raise KssCommandException(
                        'Failed to create storage pools. (Unexplained) - pool=%s' \
                        % opts.name)

                self.up_progress(20)
                # pool autostart check
                flag = True # autostart on
                if conn.autostart_storage_pool(flag) is False:
                    raise KssCommandException(
                        'Failed to autostart storage pool(libvirt). - pool=%s'
                        % (opts.name))

                ret = conn.is_autostart_storage_pool()
                if not (ret is flag):
                    raise KssCommandException(
                        'Auto-start failed to set the storage pool. - pool=%s, autostart=%s' \
                        % (opts.name, str(ret)))

                self.logger.info('Created storage pool. - pool=%s' % (opts.name))
                print >>sys.stdout, _('Created storage pool. - pool=%s') % (opts.name)
                return True
            except KssCommandException, e:
                raise e
        finally:
            conn.close()

if __name__ == "__main__":
    target = CreateStoragePool()
    sys.exit(target.run())
