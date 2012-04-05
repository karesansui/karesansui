#!/usr/bin/python
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
    from karesansui.lib.const import STORAGE_POOL_TYPE, STORAGE_VOLUME_FORMAT, \
        STORAGE_VOLUME_SIZE_MIN_LENGTH, STORAGE_VOLUME_SIZE_MAX_LENGTH, STORAGE_VOLUME_UNIT, \
        DISK_USES
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name',             dest='name',             help=_('Domain Name'),      default=None)
    optp.add_option('-p', '--pool_name',        dest='pool_name',        help=_('Pool Name'),        default=None)
    optp.add_option('-v', '--volume_name',      dest='volume_name',      help=_('Volume Name'),      default=None)
    optp.add_option('-f', '--format',           dest='format',           help=_('Format'),           default=None)
    optp.add_option('-a', '--allocation',       dest='allocation',       help=_('Allocation'),       default=0, type="int")
    optp.add_option('-c', '--capacity',         dest='capacity',         help=_('Capacity'),         default=0, type="int")
    optp.add_option('-u', '--unit',             dest='unit',             help=_('Volume Size Unit'), default="")
    optp.add_option('-o', '--permission_owner', dest='permission_owner', help=_('Permission Owner'), default=None)
    optp.add_option('-g', '--permission_group', dest='permission_group', help=_('Permission Group'), default=None)
    optp.add_option('-m', '--permission_mode',  dest='permission_mode',  help=_('Permission Mode'),  default=None)
    optp.add_option('-U', '--use',              dest='use',              help=_('Disk usage."images" or "disk"'), default=None)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.pool_name:
        if reg.search(opts.pool_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool_name', opts.pool_name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --pool_name')

    if opts.volume_name:
        if reg.search(opts.pool_name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool_name', opts.pool_name))

    if opts.format:
        if reg.search(opts.format):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-f or --format', opts.format))

        if opts.format not in STORAGE_VOLUME_FORMAT.values():
            raise KssCommandOptException('ERROR: Format is not available. '
                                         'raw or qcow2... is available. format=%s' % opts.format)
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-f or format')

    if opts.unit:
        if opts.unit not in STORAGE_VOLUME_UNIT.keys():
            raise KssCommandOptException('ERROR: Volume size unit is not available. '
                                         'K or M... is available. unit=%s' % opts.unit)

    reg = re.compile("[^0-9]")
    if opts.permission_owner:
        if reg.search(opts.permission_owner):
            if opts.permission_owner not in [user[0] for user in get_pwd_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. owner=%s' % (opts.permission_owner))
        else:
            if int(opts.permission_owner) not in [user[2] for user in get_pwd_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. owner=%s' % (opts.permission_owner))

    if opts.permission_group:
        if reg.search(opts.permission_group):
            if opts.permission_group not in [group[0] for group in get_grp_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. group=%s' % (opts.permission_group))
        else:
            if int(opts.permission_group) not in [group[2] for group in get_grp_info()]:
                raise KssCommandOptException('ERROR: Permission user not found. group=%s' % (opts.permission_group))

    reg = re.compile("^[0-9]{3,4}$")
    if opts.permission_mode:
        if not reg.match(opts.permission_mode):
            raise KssCommandOptException('ERROR: Illigal permission mode. mode=%s' % (opts.permission_mode))

    if opts.use:
        if opts.use not in DISK_USES.values():
            raise KssCommandOptException('ERROR: Disk usage is not available. '
                                         'images or disk is available. use=%s' % opts.use)

        if opts.use == DISK_USES["IMAGES"]:
            if not opts.volume_name:
                raise KssCommandOptException('ERROR: %s option is required.' % '-v or --volume_name')

class CreateStorageVolume(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        conn = KaresansuiVirtConnection(readonly=False)

        try:
            try:
                #inactive_storage_pools = conn.list_inactive_storage_pool()
                inactive_storage_pools = []
                active_storage_pools = conn.list_active_storage_pool()
                if not (opts.pool_name in active_storage_pools or \
                        opts.pool_name in inactive_storage_pools):
                    raise KssCommandException('Storage pool does not exist. Alternatively, the storage pool is not started. - pool=%s'
                                              % opts.pool_name)

                if conn.get_storage_volume(opts.pool_name, opts.volume_name) is not None:
                    raise KssCommandException(
                        'We already have a storage volume. - pool=%s, vol=%s'
                        % (opts.pool_name, opts.volume_name))

                pool_obj = conn.search_kvn_storage_pools(opts.pool_name)[0]
                pool_info = pool_obj.get_info()
                if not pool_info['allocation'] or pool_info['allocation'] == 0:
                    storage_volume_allocation_max_size = STORAGE_VOLUME_SIZE_MAX_LENGTH
                else:
                    storage_volume_allocation_max_size = long(pool_info['allocation']) / STORAGE_VOLUME_UNIT.get(opts.unit, 1)
                    if pool_info['type'] == 'dir' or pool_info['type'] == 'fs':
                        storage_volume_allocation_max_size = long(pool_info["available"]) / STORAGE_VOLUME_UNIT.get(opts.unit, 1)
                if not pool_info['capacity'] or pool_info['capacity'] == 0:
                    storage_volume_capacity_max_size = STORAGE_VOLUME_SIZE_MAX_LENGTH
                else:
                    storage_volume_capacity_max_size = long(pool_info['capacity']) / STORAGE_VOLUME_UNIT.get(opts.unit, 1)

                if opts.allocation < STORAGE_VOLUME_SIZE_MIN_LENGTH or storage_volume_allocation_max_size < opts.allocation:
                    raise KssCommandException('Allocation "%s%s" is out of available range. available=%s-%s%s'
                                              % (opts.allocation, opts.unit, STORAGE_VOLUME_SIZE_MIN_LENGTH, storage_volume_allocation_max_size, opts.unit))
                if opts.capacity < STORAGE_VOLUME_SIZE_MIN_LENGTH or storage_volume_capacity_max_size < opts.capacity:
                    raise KssCommandException('Capacity "%s%s" is out of available range. available=%s-%s%s'
                                              % (opts.capacity, opts.unit, STORAGE_VOLUME_SIZE_MIN_LENGTH, storage_volume_capacity_max_size, opts.unit))

                if conn.create_storage_volume(opts.name,
                                              opts.pool_name,
                                              opts.format,
                                              use=opts.use,
                                              volume_name=opts.volume_name,
                                              capacity=opts.capacity,
                                              allocation=opts.allocation,
                                              c_unit=opts.unit,
                                              t_p_owner=opts.permission_owner,
                                              t_p_group=opts.permission_group,
                                              t_p_mode=opts.permission_mode,
                                           ) is False:
                    raise KssCommandException('Failed to create storage volume. (libvirt) - pool=%s, vol=%s'
                                              % (opts.pool_name, opts.volume_name))

                self.up_progress(40)

                vol_path = conn.get_storage_volume_path(opts.pool_name, opts.volume_name)
                if vol_path is None:
                    raise KssCommandException(
                        'Could not get the normal storage pool or storage volume. - pool=%s, vol=%s' \
                        % (opts.pool, opts.volume_name))

                if os.path.isfile(vol_path) is False:
                    raise KssCommandException(
                        'File does not exist in the path of a storage volume. - pool=%s, vol=%s' \
                        % (opts.pool, opts.volume_name))

                vol_obj = conn.get_storage_volume(opts.pool_name, opts.volume_name)
                if vol_obj is None:
                    raise KssCommandException(
                        'Could not get the normal storage pool or storage volume. - pool=%s, vol=%s' \
                        % (opts.pool, opts.volume_name))

                vol_link = "%s/%s" % (pool_info['target']['path'], vol_obj.name())
                if os.path.islink(vol_link) is False:
                    raise KssCommandException(
                        'Symbolic link does not exist in the path of a storage volume. - pool=%s, vol=%s' \
                        % (opts.pool, opts.volume_name))

                self.logger.info('Created storage volume. - vol=%s' % (opts.volume_name))
                print >>sys.stdout, _('Created storage volume. - vol=%s') % (opts.volume_name)
                return True
            except KssCommandException, e:
                raise e
        finally:
            conn.close()

if __name__ == "__main__":
    target = CreateStorageVolume()
    sys.exit(target.run())
