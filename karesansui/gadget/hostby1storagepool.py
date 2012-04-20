# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2012 HDE, Inc.
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

import pwd

import web
from web.utils import Storage

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.const import STORAGE_POOL_TYPE, \
     VIRT_COMMAND_CREATE_STORAGE_POOL, STORAGE_VOLUME_FORMAT, \
     VIRT_COMMAND_DELETE_STORAGE_POOL, STORAGE_POOL_PWD, \
     ISCSI_DEVICE_DIR, ISCSI_COMMAND_READY_MOUNT, VENDOR_DATA_ISCSI_MOUNT_DIR

from karesansui.lib.utils import get_system_user_list

from karesansui.db.access.machine import findbyhost1
from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from karesansui.gadget.hostby1networkstorage import get_iscsi_cmd
from pysilhouette.command import dict2command

from karesansui.lib.utils import is_param
from karesansui.lib.checker import Checker, CHECK_EMPTY, CHECK_ONLYSPACE, CHECK_STARTROOT, \
    CHECK_NOTROOT

# validate
def validates_pool_dir(obj, now_pools):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'pool_name'):
        check = checker.check_string(_('Storage Pool Name'),
                                     obj.input.pool_name,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     ) and check
        if obj.input.pool_name in now_pools:
            check = False
            checker.add_error(_('%s "%s" already exists.') % (_('Storage Pool Name'), obj.input.pool_name))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Storage Pool Name'))

    if is_param(obj.input, 'pool_target_path'):
        check = checker.check_directory(_('Directory Path'),
                                        obj.input.pool_target_path,
                                        CHECK_EMPTY | CHECK_STARTROOT | CHECK_NOTROOT
                                        ) and check
        try:
            kvc = KaresansuiVirtConnection()

            for pool_name in now_pools:
                target_path = kvc.get_storage_pool_targetpath(pool_name)
                if obj.input.pool_target_path == target_path:
                    check = False
                    checker.add_error(_('Storagepool target path "%s" is already being used.') % (obj.input.pool_target_path))
        finally:
            kvc.close()

    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Directory Path'))

    obj.view.alert = checker.errors
    return check

def validates_pool_iscsi(obj, now_pools):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'pool_name'):
        check = checker.check_string(_('Storage Pool Name'),
                                     obj.input.pool_name,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     ) and check
        if obj.input.pool_name in now_pools:
            check = False
            checker.add_error(_('%s "%s" already exists.') % (_('Storage Pool Name'), obj.input.pool_name))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Storage Pool Name'))

    if is_param(obj.input, 'pool_target_iscsi'):
        check = checker.check_string(_('iSCSI Target'),
                                        obj.input.pool_target_iscsi,
                                        CHECK_EMPTY | CHECK_ONLYSPACE,
                                        None,
                                        ) and check
        try:
            kvc = KaresansuiVirtConnection()

            for pool_name in now_pools:
                pool_iqn = kvc.get_storage_pool_sourcedevicepath(pool_name)
                if obj.input.pool_target_iscsi == pool_iqn:
                    check = False
                    checker.add_error(_('Storagepool iSCSI target IQN "%s" is already being used.') % (obj.input.pool_target_iscsi))
        finally:
            kvc.close()

    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('iSCSI Target'))

    obj.view.alert = checker.errors
    return check

# create job
def create_pool_dir_job(obj, machine, name, type_, target_path,
                        options={}, rollback_options={}):
    cmdname = u"Create Storage Pool"
    cmd = VIRT_COMMAND_CREATE_STORAGE_POOL

    options['name'] = name
    options["type"] = type_
    options["target_path"] = target_path
    options["mode"] = STORAGE_POOL_PWD["MODE"]
    options["group"] = pwd.getpwnam(STORAGE_POOL_PWD["GROUP"])[2]
    options["owner"] = pwd.getpwnam(STORAGE_POOL_PWD["OWNER"])[2]

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)


    rollback_options["name"] = name

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_POOL),
        rollback_options)

    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _job = Job('%s command' % cmdname, 0, _cmd)

    _job.rollback_command = rollback_cmd
    _jobgroup.jobs.append(_job)

    _machine2jobgroup = m2j_new(machine=machine,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )
    return True

# create job
def create_pool_iscsi_job(obj, machine, name, type_, host_name, device_path, automount_list,
                          options={}, rollback_options={}):
    cmdname = u"Create Storage Pool"
    cmd = VIRT_COMMAND_CREATE_STORAGE_POOL

    options['name'] = name
    options["type"] = type_
    options["host_name"] = host_name
    options["device_path"] = device_path

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    rollback_options["name"] = name
    rollback_options["force"] = None
    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_POOL),
        rollback_options)

    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    _job = Job('%s command' % cmdname, 0, _cmd)
    _job.rollback_command = rollback_cmd
    _jobgroup.jobs.append(_job)

    _machine2jobgroup = m2j_new(machine=machine,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )

    automount_options = {}
    automount_options["type"] = STORAGE_POOL_TYPE['TYPE_FS']

    for disk in automount_list:
        readymount_options = {}
        readymount_options["dev"] = "%s/%s" % (ISCSI_DEVICE_DIR, disk['symlink_name'])
        if "is_format" in disk:
            readymount_options["format"] = None

        automount_options["name"] = disk['symlink_name']
        automount_options["device_path"] = "%s/%s" % (ISCSI_DEVICE_DIR, disk['symlink_name'])
        automount_options["target_path"] = "%s/%s" % (VENDOR_DATA_ISCSI_MOUNT_DIR, disk['symlink_name'])

        readymount_cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], ISCSI_COMMAND_READY_MOUNT), readymount_options)
        readymount_job = Job('Check mount command', 0, readymount_cmd)

        automount_cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'], cmd), automount_options)
        automount_job = Job('%s command' % cmdname, 1, automount_cmd)

        jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
        jobgroup.jobs.append(readymount_job)
        jobgroup.jobs.append(automount_job)

        machine2jobgroup = m2j_new(machine=machine,
                                    jobgroup_id=-1,
                                    uniq_key=karesansui.sheconf['env.uniqkey'],
                                    created_user=obj.me,
                                    modified_user=obj.me,
                                    )

        save_job_collaboration(obj.orm,
                               obj.pysilhouette.orm,
                               machine2jobgroup,
                               jobgroup,
                               )

    return True

class HostBy1StoragePool(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id

        # Pool
        try:
            kvc = KaresansuiVirtConnection()
            inactive_pool = kvc.list_inactive_storage_pool()
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            self.view.pools = pools
            pools_info = []
            for pool in pools:
                pool_obj = kvc.search_kvn_storage_pools(pool)[0]
                pools_info.append(pool_obj.get_info())
                if pool_obj.is_active() is True:
                    vols_obj = pool_obj.search_kvn_storage_volumes(kvc)

                    vols_info = []
                    for vol_obj in vols_obj:
                        vols_info.append(vol_obj.get_info())
        finally:
            kvc.close()

        self.view.pools_info = pools_info

        if self.is_mode_input() is True:
            # .input
            try:
                kvc = KaresansuiVirtConnection()

                already_iqn = []
                for pool in pools:
                    pool_iqn = kvc.get_storage_pool_sourcedevicepath(pool)
                    if pool_iqn:
                        already_iqn.append(pool_iqn)
            finally:
                kvc.close()

            network_storages = get_iscsi_cmd(self, host_id)
            if network_storages is False:
                self.logger.debug("Get iSCSI command failed. Return to timeout")
                return web.internalerror('Internal Server Error. (Timeout)')

            available_network_storages = []
            for i in range(len(network_storages)):
                if network_storages[i]['iqn'] not in already_iqn and network_storages[i]['activity'] == 1:
                    available_network_storages.append(network_storages[i])

            self.view.network_storages = available_network_storages
            self.view.pool_types = (STORAGE_POOL_TYPE["TYPE_DIR"],
                                    STORAGE_POOL_TYPE["TYPE_ISCSI"])

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id

        model = findbyhost1(self.orm, host_id)

        # virt
        kvc = KaresansuiVirtConnection()
        try:
            inactive_pool = kvc.list_inactive_storage_pool()
            active_pool = kvc.list_active_storage_pool()
        finally:
            kvc.close()

        now_pools = inactive_pool + active_pool
        if self.input.pool_type == STORAGE_POOL_TYPE["TYPE_DIR"]:
            if not validates_pool_dir(self, now_pools):
                return web.badrequest(self.view.alert)

            extra_opts = {}
            if create_pool_dir_job(self,
                                   model,
                                   self.input.pool_name,
                                   self.input.pool_type,
                                   self.input.pool_target_path,
                                   extra_opts) is True:
                self.logger.debug("Create dir storage pool success.")
                return web.accepted()
            else:
                self.logger.debug("Failed create DIR storage pool job.")
                return False
        elif self.input.pool_type == STORAGE_POOL_TYPE["TYPE_ISCSI"]:
            if not validates_pool_iscsi(self, now_pools):
                return web.badrequest(self.view.alert)
            extra_opts = {}
            network_storages = get_iscsi_cmd(self, host_id)
            if network_storages is False:
                self.logger.debug("Get iSCSI command failed. Return to timeout")
                return web.internalerror('Internal Server Error. (Timeout)')

            pool_host_name = None
            pool_device_path = None
            for iscsi in network_storages:
                if self.input.pool_target_iscsi == iscsi["iqn"]:
                    pool_host_name = iscsi["hostname"]
                    pool_device_path = iscsi["iqn"]
                    disk_list = iscsi["disk_list"]
                    break

            if pool_host_name is None or pool_device_path is None:
                self.logger.debug("Failed create iSCSI storage pool. Target iSCSI device not found.")
                return web.badrequest()

            automount_list = []
            for disk in disk_list:
                if is_param(self.input, "iscsi-disk-use-type-%s" % (disk['symlink_name'])):
                    if self.input["iscsi-disk-use-type-%s" % (disk['symlink_name'])] == "mount" and disk['is_partitionable'] is False:
                        if is_param(self.input, "iscsi-disk-format-%s" % (disk['symlink_name'])):
                            if self.input["iscsi-disk-format-%s" % (disk['symlink_name'])] == "true":
                                disk["is_format"] = True
                        automount_list.append(disk)

            if create_pool_iscsi_job(self,
                                     model,
                                     self.input.pool_name,
                                     self.input.pool_type,
                                     pool_host_name,
                                     pool_device_path,
                                     automount_list,
                                     extra_opts) is True:
                self.logger.debug("Create iSCSI storage pool success. name=%s" % (self.input.pool_name))
                return web.accepted()
            else:
                self.logger.debug("Failed create iSCSI storage pool job. name=%s" % (self.input.pool_name))
                return False
        else:
            self.logger.debug("Non-existent type. type=%s" % self.input.pool_type)
            return web.badrequest("Non-existent type. type=%s" % self.input.pool_type)

urls = (
    '/host/(\d+)/storagepool/?(\.part)$', HostBy1StoragePool,
    )
