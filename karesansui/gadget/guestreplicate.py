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

import web
import simplejson as json

import karesansui
#from karesansui.gadget.guest import regist_guest
from karesansui.gadget.guestby1disk import create_disk_job

from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import \
    VIRT_COMMAND_REPLICATE_GUEST, \
    VNC_PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
    ID_MIN_LENGTH, ID_MAX_LENGTH, MACHINE_ATTRIBUTE

from karesansui.lib.utils import comma_split, generate_uuid, \
    string_from_uuid, is_param, uni_force, \
    next_number, generate_mac_address, chk_create_disk, get_partition_info
from karesansui.db.access.machine import findbyguest1, new as m_new
from karesansui.db.access.tag import new as t_new
from karesansui.db.access.notebook import new as n_new
from karesansui.lib.virt.virt import KaresansuiVirtConnection

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_ONLYSPACE, \
    CHECK_MIN, CHECK_MAX

from karesansui.lib.const import \
    NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH, \
    MACHINE_NAME_MIN_LENGTH, MACHINE_NAME_MAX_LENGTH, \
    TAG_MIN_LENGTH, TAG_MAX_LENGTH, \
    VNC_PORT_MIN_NUMBER, VNC_PORT_MAX_NUMBER, \
    DOMAIN_NAME_MIN_LENGTH, DOMAIN_NAME_MAX_LENGTH, \
    VIRT_COMMAND_DELETE_GUEST, VIRT_COMMAND_REPLICATE_STORAGE_VOLUME, \
    DISK_USES, VIRT_COMMAND_DELETE_STORAGE_VOLUME

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.access._2pysilhouette import jg_save, jg_delete
from karesansui.db.model._2pysilhouette import Job, JobGroup
from karesansui.db.access.machine import \
     findbyhost1guestall, findbyhost1, \
     findbyguest1, \
     new as m_new, save as m_save, delete as m_delete

from karesansui.db.access.machine2jobgroup import new as m2j_new, save as m2j_save

from pysilhouette.command import dict2command

def validates_guest_replicate(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'm_name'):
        check = False
        checker.add_error(_('Parameter m_name does not exist.'))
    else:
        check = checker.check_string(
                    _('Machine Name'),
                    obj.input.m_name,
                    CHECK_EMPTY | CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = MACHINE_NAME_MIN_LENGTH,
                    max = MACHINE_NAME_MAX_LENGTH,
            ) and check

    if is_param(obj.input, 'note_title'):
        check = checker.check_string(
                    _('Title'),
                    obj.input.note_title,
                    CHECK_LENGTH | CHECK_ONLYSPACE,
                    None,
                    min = NOTE_TITLE_MIN_LENGTH,
                    max = NOTE_TITLE_MAX_LENGTH,
                ) and check

    if is_param(obj.input, 'note_value'):
        check = checker.check_string(
                    _('Note'),
                    obj.input.note_value,
                    CHECK_ONLYSPACE,
                    None,
                    None,
                    None,
                ) and check

    if is_param(obj.input, 'tags'):
        for tag in comma_split(obj.input.tags):
            check = checker.check_string(
                        _('Tag'),
                        tag,
                        CHECK_LENGTH | CHECK_ONLYSPACE,
                        None,
                        min = TAG_MIN_LENGTH,
                        max = TAG_MAX_LENGTH,
                    ) and check

    if not is_param(obj.input, 'domain_dest_name'):
        check = False
        checker.add_error(_('Parameter domain_dest_name does not exist.'))
    else:
        check = checker.check_string(
                _('Destination Domain Name'),
                obj.input.domain_dest_name,
                CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH,
                '[^-a-zA-Z0-9_\.]+',
                DOMAIN_NAME_MIN_LENGTH,
                DOMAIN_NAME_MAX_LENGTH,
            ) and check

    if not is_param(obj.input, 'vm_vncport'):
        check = False
        checker.add_error(_('Parameter vm_vncport does not exist.'))
    else:
        check = checker.check_number(
                _('VNC Port Number'),
                obj.input.vm_vncport,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                VNC_PORT_MIN_NUMBER,
                VNC_PORT_MAX_NUMBER,
            ) and check

    if not is_param(obj.input, 'vm_mac'):
        check = False
        checker.add_error(_('Parameter vm_mac does not exist.'))
    else:
        check = checker.check_macaddr(
                _('MAC Address'),
                obj.input.vm_mac,
                CHECK_EMPTY | CHECK_VALID,
            ) and check

    obj.view.alert = checker.errors
    return check


def validates_src_id(obj):
    """<comment-ja>
    ゲストOSコピー元のチェッカー
    @param obj: karesansui.lib.rest.Rest オブジェクト
    @type obj: karesansui.lib.rest.Rest
    @return: check
    @rtype: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if not is_param(obj.input, 'src_id'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Copy Source'))
    else:
        check = checker.check_number(_('Copy Source'),
                                     obj.input.src_id,
                                     CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     ID_MIN_LENGTH,
                                     ID_MAX_LENGTH
                                     ) and check

        obj.view.alert = checker.errors
    return check


def replicate_storage_volume(obj, orig_name, orig_pool, orig_volume,
                             dest_name, dest_pool, dest_volume,
                             order):
    """
    <comment-ja>
    ゲストOSに登録されているディスク(ストレージボリューム)のコピージョブを作成します。
    </comment-ja>
    <comment-en>
    TODO: English Documents(en)
    </comment-en>
    """
    cmdname = u"Replicate Storage_Volume %s" % dest_name
    cmd = VIRT_COMMAND_REPLICATE_STORAGE_VOLUME

    options = {}

    options["orig_name"] = orig_name
    options["orig_pool"] = orig_pool
    options["orig_volume"] = orig_volume
    options["dest_name"] = dest_name
    options["dest_pool"] = dest_pool
    options["dest_volume"] = dest_volume

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    rollback_options = {}

    rollback_options["name"] = dest_volume
    rollback_options["pool_name"] = dest_pool
    rollback_options["use"] = DISK_USES["DISK"]

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_VOLUME),
        rollback_options)

    job = Job('%s command' % cmdname, order, _cmd)
    job.rollback_command = rollback_cmd
    return job

def replicate_guest(obj, guest, cmd, options, cmdname, rollback_options, order):
    if (karesansui.sheconf.has_key('env.uniqkey') is False) \
           or (karesansui.sheconf['env.uniqkey'].strip('') == ''):
        raise

    action_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd),
        options)

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_GUEST),
        rollback_options)

    job = Job(cmdname, order, action_cmd)
    job.rollback_command = rollback_cmd
    return job

def exec_replicate_guest(obj, _guest, icon_filename, cmdname,
                         guest_job, disk_jobs, volume_jobs):

    if icon_filename:
        _guest.icon = icon_filename

    if (karesansui.sheconf.has_key('env.uniqkey') is False) \
           or (karesansui.sheconf['env.uniqkey'].strip('') == ''):
        raise

    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])

    _jobgroup.jobs.extend(volume_jobs)
    _jobgroup.jobs.append(guest_job)
    _jobgroup.jobs.extend(disk_jobs)

    # GuestOS INSERT
    try:
        m_save(obj.orm, _guest)
        obj.orm.commit()
    except:
        obj.logger.error('Failed to register the Guest OS. #1 - guest name=%s' \
                          % _guest.name)
        raise # throw

    # JobGroup INSERT
    try:
        jg_save(obj.pysilhouette.orm, _jobgroup)
        obj.pysilhouette.orm.commit()
    except:
        # rollback(machine)
        obj.logger.error('Failed to register the JobGroup. #2 - jobgroup name=%s' \
                          % _jobgroup.name)

        try:
            m_delete(obj.orm, _guest)
            obj.orm.commit()
            obj.logger.error('#3 Rollback successful. - guest id=%d' % _guest.id)
        except:
            obj.logger.critical('#4 Rollback failed. - guest id=%d' % _guest.id)
            raise

        raise # throw

    # Machine2JobGroup INSERT
    try:
        _m2j = m2j_new(machine=_guest,
                       jobgroup_id=_jobgroup.id,
                       uniq_key=karesansui.sheconf['env.uniqkey'],
                       created_user=obj.me,
                       modified_user=obj.me,
                       )
        m2j_save(obj.orm, _m2j)
        obj.orm.commit()
    except:
        # rollback(machine, jobgroup)
        try:
            m_delete(obj.orm, _guest)
            obj.orm.commit()
        except:
            # rollback(machine)
            obj.logger.critical('Failed to register the Machine. #5 - guest id=%d' \
                              % _guest.id)
        try:
            jg_delete(obj.pysilhouette.orm, _jobgroup)
            obj.pysilhouette.orm.commit()
        except:
            # rollback(jobgroup)
            obj.logger.critical('Failed to register the JobGroup. #6 - jobgroup id=%d' \
                              % _jobgroup.id)
        raise # throw

    return True

class GuestReplicate(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_src_id(self):
            self.view.alert = "Failed to get the id of source domain."
            self.logger.debug(self.view.alert)
            return web.badrequest(self.view.alert)

        src_id = self.input.src_id
        if self.is_mode_input() is False:
            return web.nomethod()

        self.view.src_id = src_id
        self.view.mac_address = generate_mac_address()

        src_guest = findbyguest1(self.orm, src_id)
        if not src_guest:
            self.view.alert = "Failed to get the data of source domain."
            self.logger.debug(self.view.alert)
            return web.badrequest(self.view.alert)

        kvc = KaresansuiVirtConnection()
        try:
            # Storage Pool
            #inactive_pool = self.kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            domname = kvc.uuid_to_domname(src_guest.uniq_key)

            # TODO 対応するストレージボリュームにiscsiがあった場合はエラーにする
            src_pools = kvc.get_storage_pool_name_bydomain(domname)
            if not src_pools:
                self.view.alert = _("Source storage pool is not found.")
                self.logger.debug(self.view.alert)
                return web.badrequest(self.view.alert)

            for src_pool in  src_pools :
                src_pool_type = kvc.get_storage_pool_type(src_pool)
                if src_pool_type != 'dir':
                    self.view.alert = _("'%s' disk contains the image.") % (src_pool_type)
                    self.logger.debug(self.view.alert)
                    return web.badrequest(self.view.alert)

            non_iscsi_pool = []
            for pool in pools:
                if kvc.get_storage_pool_type(pool) != 'iscsi':
                    non_iscsi_pool.append(pool)
            self.view.pools = non_iscsi_pool

            virt = kvc.search_kvg_guests(domname)[0]
            if virt.is_active() is True:
                self.view.alert = _("Guest is running. Please stop and try again. name=%s" % domname)
                self.logger.debug(self.view.alert)
                return web.badrequest(self.view.alert)

            self.view.domain_src_name = virt.get_domain_name()
            used_ports = kvc.list_used_vnc_port()
            self.view.vnc_port = next_number(VNC_PORT_MIN_NUMBER,PORT_MAX_NUMBER,used_ports)
        finally:
            kvc.close()

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_guest_replicate(self):
            self.logger.debug(self.view.alert)
            return web.badrequest(self.view.alert)

        uuid = string_from_uuid(generate_uuid())

        # TODO dest_pool valid
        if not validates_src_id(self):
            self.logger.debug(self.view.alert)
            return web.badrequest(self.view.alert)

        src_guest = findbyguest1(self.orm, self.input.src_id)
        if not src_guest:
            self.view.alert = "Failed to get the data of source domain."
            self.logger.debug(self.view.alert)
            return web.badrequest(self.view.alert)

        # Note
        note_title = None
        if is_param(self.input, "note_title"):
            note_title = self.input.note_title

        note_value = None
        if is_param(self.input, "note_value"):
            note_value = self.input.note_value

        _notebook = n_new(note_title, note_value)

        # Tag
        _tags = None
        if is_param(self.input, "tags"):
            _tags = []
            for x in comma_split(self.input.tags):
                _tags.append(t_new(x))

        # Icon
        icon_filename = None
        if is_param(self.input, "icon_filename", empty=True):
            icon_filename = self.input.icon_filename

        dest_guest = m_new(created_user=self.me,
                           modified_user=self.me,
                           uniq_key=uni_force(uuid),
                           name=self.input.m_name,
                           attribute=MACHINE_ATTRIBUTE['GUEST'],
                           hypervisor=src_guest.hypervisor,
                           notebook=_notebook,
                           tags=_tags,
                           icon=icon_filename,
                           is_deleted=False,
                           parent=src_guest.parent,
                           )


        kvc = KaresansuiVirtConnection()
        try:
            domname = kvc.uuid_to_domname(src_guest.uniq_key)
            if not domname: return web.conflict(web.ctx.path)
            virt = kvc.search_kvg_guests(domname)[0]
            options = {}
            options["src-name"] = virt.get_domain_name()
            if is_param(self.input, "dest_pool"):
                options["pool"] = self.input.dest_pool
            if is_param(self.input, "domain_dest_name"):
                options["dest-name"] = self.input.domain_dest_name
            if is_param(self.input, "vm_vncport"):
                options["vnc-port"] = self.input.vm_vncport
            if is_param(self.input, "vm_mac"):
                options["mac"] = self.input.vm_mac

            options["uuid"] = uuid

            src_pools = kvc.get_storage_pool_name_bydomain(domname)
            if not src_pools:
                self.view.alert = _("Source storage pool is not found.")
                self.logger.debug(self.view.alert)
                return web.badrequest(self.view.alert)

            for src_pool in  src_pools :
                src_pool_type = kvc.get_storage_pool_type(src_pool)
                if src_pool_type != 'dir':
                    self.view.alert = _("'%s' disk contains the image.") % src_pool_type
                    self.logger.debug(self.view.alert)
                    return web.badrequest(self.view.alert)

            # disk check
            target_pool = kvc.get_storage_pool_name_bydomain(domname, 'os')[0]
            target_path = kvc.get_storage_pool_targetpath(target_pool)
            src_disk = "%s/%s/images/%s.img" % \
                                      (target_path, options["src-name"], options["src-name"])

            s_size = os.path.getsize(src_disk) / (1024 * 1024) # a unit 'MB'

            if os.access(target_path, os.F_OK):
                if chk_create_disk(target_path, s_size) is False:
                    partition = get_partition_info(target_path, header=False)
                    self.view.alert = _("No space available to create disk image in '%s' partition.") % partition[5][0]
                    self.logger.debug(self.view.alert)
                    return web.badrequest(self.view.alert)

            #else: # Permission denied
                #TODO:check disk space for root

            active_guests = kvc.list_active_guest()
            inactive_guests = kvc.list_inactive_guest()
            used_vnc_ports = kvc.list_used_vnc_port()
            used_mac_addrs = kvc.list_used_mac_addr()

            conflict_location = "%s/host/%d/guest/%d.json" \
                                % (web.ctx.homepath, src_guest.parent_id, src_guest.id)
            # source guestos
            if not (options["src-name"] in active_guests or options["src-name"] in inactive_guests):
                return web.conflict(conflict_location, "Unable to get the source guest.")

            # Check on whether value has already been used
            # destination guestos
            if (options["dest-name"] in active_guests or options["dest-name"] in inactive_guests):
                return web.conflict(conflict_location, "Destination guest %s is already there." % options["dest-name"])
            # VNC port number
            if(int(self.input.vm_vncport) in used_vnc_ports):
                return web.conflict(conflict_location, "VNC port %s is already used." % self.input.vm_vncport)
            # MAC address
            if(self.input.vm_mac in used_mac_addrs):
                return web.conflict(conflict_location, "MAC address %s is already used." % self.input.vm_mac)

            # Replicate Guest
            order = 0 # job order
            disk_jobs = [] # Add Disk
            volume_jobs = [] # Create Storage Volume
            for disk in virt.get_disk_info():
                if disk['type'] != 'file':
                    self.view.alert = _("The type of the storage pool where the disk is to be added must be 'file'. dev=%s") % disk['target']['dev']
                    self.logger.debug(self.view.alert)
                    return web.badrequest(self.view.alert)

                disk_pool = kvc.get_storage_pool_name_byimage(disk['source']['file'])
                if not disk_pool:
                    self.view.alert = _("Can not find the storage pool.")
                    self.logger.debug(self.view.alert)
                    return web.badrequest(self.view.alert)
                else:
                    disk_pool = disk_pool[0]

                disk_volumes = kvc.get_storage_volume_bydomain(domname, 'disk', 'key')
                volume = None
                for key in disk_volumes.keys():
                    if disk['source']['file'] == os.path.realpath(disk_volumes[key]):
                        volume = key # disk image

                if volume is None: # os image
                    continue

                disk_uuid = string_from_uuid(generate_uuid())

                volume_jobs.append(replicate_storage_volume(self,
                                                     domname,
                                                     disk_pool,
                                                     volume,
                                                     self.input.domain_dest_name,
                                                     #self.input.dest_pool,
                                                     disk_pool, # orig
                                                     disk_uuid,
                                                     order))
                order += 1

                disk_jobs.append(create_disk_job(self,
                                                 dest_guest,
                                                 self.input.domain_dest_name,
                                                 disk_pool,
                                                 disk_uuid,
                                                 bus=disk['target']['bus'],
                                                 format=disk['driver']['type'],
                                                 type=disk['type'],
                                                 target=disk['target']['dev'],
                                                 order=-1))

        finally:
            kvc.close()


        # replicate guest
        guest_job = replicate_guest(self,
                                    dest_guest,
                                    VIRT_COMMAND_REPLICATE_GUEST,
                                    options,
                                    'Replicate Guest',
                                    {"name" : options['dest-name'],
                                     "pool" : options["pool"],
                                     },
                                    order,
                                    )
        order += 1
        for disk_job in disk_jobs:
            disk_job.order = order
            order += 1

        ret = exec_replicate_guest(self,
                                   dest_guest,
                                   icon_filename,
                                   'Replicate Guest',
                                   guest_job,
                                   disk_jobs,
                                   volume_jobs,
                                   )

        if ret is True:
            return web.accepted()
        else:
            return False

urls = (
    '/host/(\d+)/guest/replicate/?$', GuestReplicate,
    )
