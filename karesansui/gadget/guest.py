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

import re
import pwd
import os.path
import glob
import time

import web

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.const import ICON_DIR_TPL, \
     VIRT_COMMAND_CREATE_GUEST, VIRT_COMMAND_REPLICATE_GUEST, \
     VIRT_COMMAND_DELETE_GUEST, \
     GRAPHICS_PORT_MIN_NUMBER, PORT_MAX_NUMBER, \
     MEMORY_MIN_SIZE, DISK_MIN_SIZE, \
     VIRT_DOMAINS_DIR, DEFAULT_KEYMAP

from karesansui.lib.const import XEN_KEYMAP_DIR, KVM_KEYMAP_DIR, KVM_BRIDGE_PREFIX

from karesansui.lib.utils import comma_split, \
     generate_mac_address, is_param, \
     next_number, generate_uuid, string_from_uuid, uniq_sort, \
     uni_force, get_partition_info, chk_create_disk, json_dumps, \
     get_ifconfig_info, get_keymaps, available_virt_mechs, \
     available_virt_uris, is_iso9660_filesystem_format, \
     get_dom_list, get_dom_type, base64_encode, \
     uri_split, uri_join, dict_search

from karesansui.lib.utils import get_xml_parse as XMLParse
from karesansui.lib.utils import get_xml_xpath as XMLXpath
from karesansui.lib.utils import get_nums_xml_xpath as XMLXpathNum
from karesansui.lib.file.configfile import ConfigFile

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_LENGTH, CHECK_ONLYSPACE, \
    CHECK_MIN, CHECK_MAX, CHECK_EXIST

from karesansui.lib.const import \
    NOTE_TITLE_MIN_LENGTH, NOTE_TITLE_MAX_LENGTH, \
    MACHINE_NAME_MIN_LENGTH, MACHINE_NAME_MAX_LENGTH, \
    TAG_MIN_LENGTH, TAG_MAX_LENGTH, \
    GRAPHICS_PORT_MIN_NUMBER, GRAPHICS_PORT_MAX_NUMBER, \
    HYPERVISOR_MIN_SIZE, HYPERVISOR_MAX_SIZE, \
    MEMORY_MIN_SIZE, DISK_MIN_SIZE, \
    DOMAIN_NAME_MIN_LENGTH, DOMAIN_NAME_MAX_LENGTH, \
    MACHINE_HYPERVISOR, MACHINE_ATTRIBUTE, \
    DISK_QEMU_FORMAT, DISK_NON_QEMU_FORMAT, \
    VIRT_COMMAND_CREATE_STORAGE_VOLUME, \
    VIRT_COMMAND_DELETE_STORAGE_VOLUME, STORAGE_VOLUME_PWD, \
    DISK_USES

from karesansui.lib.virt.virt import KaresansuiVirtConnection, KaresansuiVirtConnectionAuth
from karesansui.lib.virt.config_export import ExportConfigParam

from karesansui.lib.merge import  MergeGuest, MergeHost

from karesansui.db.access.machine import \
     findbyhost1guestall, findbyhost1, \
     findbyguest1, \
     new as m_new, save as m_save, delete as m_delete

from karesansui.db.access.machine2jobgroup import new as m2j_new, save as m2j_save
from karesansui.db.access.notebook import new as n_new
#from karesansui.db.access.tag import new as t_new, samecount as t_count, findby1name as t_name
from karesansui.db.access.tag import new as t_new, samecount as t_count, findby1name as t_name
from karesansui.db.access._2pysilhouette import jg_save, jg_delete
from karesansui.db.model._2pysilhouette import Job, JobGroup

from pysilhouette.command import dict2command

def validates_guest_add(obj):
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


    if not is_param(obj.input, 'm_hypervisor'):
        check = False
        checker.add_error(_('Parameter m_hypervisor does not exist.'))
    else:
        check = checker.check_hypervisor(
                _('Hypervisor'),
                obj.input.m_hypervisor,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                HYPERVISOR_MIN_SIZE,
                HYPERVISOR_MAX_SIZE,
            ) and check

    if not is_param(obj.input, 'domain_name'):
        check = False
        checker.add_error(_('Parameter domain_name does not exist.'))
    else:
        check = checker.check_string(
                _('Domain Name'),
                obj.input.domain_name,
                CHECK_EMPTY | CHECK_VALID | CHECK_LENGTH | CHECK_ONLYSPACE,
                '[^-a-zA-Z0-9_\.]+',
                DOMAIN_NAME_MIN_LENGTH,
                DOMAIN_NAME_MAX_LENGTH,
            ) and check

        if obj.input.domain_name in get_dom_list():
            dom_type = get_dom_type(obj.input.domain_name)
            checker.add_error(_("The same domain name already exists for hypervisor '%s'.") % dom_type.upper())
            check = False

    if is_param(obj.input, 'vm_mem_size'):
        check = checker.check_number(
                _('Memory Size (MB)'),
                obj.input.vm_mem_size,
                CHECK_VALID | CHECK_MIN | CHECK_EMPTY,
                MEMORY_MIN_SIZE,
                None,
            ) and check

    if is_param(obj.input, 'pool_type'):
        if obj.input.pool_type != "block":
            if is_param(obj.input, 'vm_disk_size'):
                check = checker.check_number(
                        _('Disk Size (MB)'),
                        obj.input.vm_disk_size,
                        CHECK_VALID | CHECK_MIN | CHECK_EMPTY,
                        DISK_MIN_SIZE,
                        None,
                ) and check

    if not is_param(obj.input, 'boot_image'):
        check = False
        checker.add_error(_('Parameter boot_image does not exist.'))
    else:
        if obj.input.boot_image == "kernel":
            if not is_param(obj.input, 'vm_kernel'):
                check = False
                checker.add_error(_('Parameter vm_kernel does not exist.'))
            else:
                check = checker.check_startfile(
                        _('Kernel Image'),
                        obj.input.vm_kernel,
                        CHECK_EMPTY | CHECK_VALID | CHECK_EXIST,
                    ) and check

            if not is_param(obj.input, 'vm_initrd'):
                check = False
                checker.add_error(_('Parameter vm_initrd does not exist.'))
            else:
                check = checker.check_startfile(
                        _('Initrd Image'),
                        obj.input.vm_initrd,
                        CHECK_EMPTY | CHECK_VALID | CHECK_EXIST,
                    ) and check

        if obj.input.boot_image == "iso":
            if not is_param(obj.input, 'vm_iso'):
                check = False
                checker.add_error(_('Parameter vm_iso does not exist.'))
            else:
                check = checker.check_startfile(
                        _('ISO Image'),
                        obj.input.vm_iso,
                        CHECK_EMPTY | CHECK_VALID | CHECK_EXIST,
                    ) and check
                if check:
                    check = is_iso9660_filesystem_format(obj.input.vm_iso)
                    checker.add_error(_('"%s" is not valid ISO 9660 CD-ROM filesystem data.') % obj.input.vm_iso)

    if not is_param(obj.input, 'keymap'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Graphics Keymap'))
    else:
        hypervisor = "KVM"
        if int(obj.input.m_hypervisor) == MACHINE_HYPERVISOR['XEN']:
            hypervisor = "XEN"
        elif int(obj.input.m_hypervisor) == MACHINE_HYPERVISOR['KVM']:
            hypervisor = "KVM"
        check = checker.check_keymap(
                _('Graphics Keymap'),
                obj.input.keymap,
                CHECK_EMPTY | CHECK_EXIST,
                hypervisor
                ) and check

    if not is_param(obj.input, 'vm_graphics_port'):
        check = False
        checker.add_error(_('Parameter vm_graphics_port does not exist.'))
    else:
        check = checker.check_number(
                _('Graphics Port Number'),
                obj.input.vm_graphics_port,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                GRAPHICS_PORT_MIN_NUMBER,
                GRAPHICS_PORT_MAX_NUMBER,
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


# public method
def make_storage_volume_job(uuid, name, pool_name, format,
                            capacity, allocation, unit, order):
    cmdname = u"Create Storage Volume"
    cmd = VIRT_COMMAND_CREATE_STORAGE_VOLUME

    options = {}
    options['volume_name'] = uuid
    options['name'] = name
    options['pool_name'] = pool_name
    options['format'] = format
    options['capacity'] = capacity
    options['allocation'] = allocation
    options['unit'] = unit
    options['permission_owner'] = pwd.getpwnam(STORAGE_VOLUME_PWD["OWNER"])[2]
    options['permission_group'] = pwd.getpwnam(STORAGE_VOLUME_PWD["GROUP"])[2]
    options['permission_mode'] = STORAGE_VOLUME_PWD["MODE"]
    options['use'] = DISK_USES["IMAGES"]

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    rollback_options = {}
    #rollback_options["name"] = name
    rollback_options["name"] = uuid
    rollback_options["pool_name"] = pool_name
    rollback_options["use"] = DISK_USES["IMAGES"]

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_STORAGE_VOLUME),
        rollback_options)

    _job = Job('%s command' % cmdname, order, _cmd)
    # delete_guestコマンドが削除まで担当してくれるので、ここではロールバックコマンドを設定しない。
    #_job.rollback_command = rollback_cmd
    return _job

def regist_guest(obj, _guest, icon_filename,
                  cmd, options, cmdname, rollback_options, is_create=False):

    if icon_filename:
        _guest.icon = icon_filename

    if (karesansui.sheconf.has_key('env.uniqkey') is False) \
           or (karesansui.sheconf['env.uniqkey'].strip('') == ''):
        raise 

    action_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd),
        options)

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], VIRT_COMMAND_DELETE_GUEST),
        rollback_options)

    _jobgroup = JobGroup(cmdname[0], karesansui.sheconf['env.uniqkey'])

    # create volume job
    order = 0
    if is_create is True:
        _volume_job = make_storage_volume_job(options["uuid"],
                                              options["storage-volume"],
                                              options["storage-pool"],
                                              options["disk-format"],
                                              options["disk-size"],
                                              options["disk-size"],
                                              'M',
                                              order
                                              )

        order += 1
        _jobgroup.jobs.append(_volume_job)


    _job = Job('%s command' % cmdname[1], order, action_cmd)
    _job.rollback_command = rollback_cmd
    _jobgroup.jobs.append(_job)

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

class Guest(Rest):

    def _post(self, f):
        ret = Rest._post(self, f)
        if hasattr(self, "kvc") is True:
            self.kvc.close()
        return ret

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        model = findbyhost1(self.orm, host_id)
        uris = available_virt_uris()

        #import pdb; pdb.set_trace()
        if model.attribute == MACHINE_ATTRIBUTE["URI"]:
            uri_guests = []
            uri_guests_status = {}
            uri_guests_kvg = {}
            uri_guests_info = {}
            uri_guests_name = {}
            segs = uri_split(model.hostname)
            uri = uri_join(segs, without_auth=True)
            creds = ''
            if segs["user"] is not None:
                creds += segs["user"]
                if segs["passwd"] is not None:
                    creds += ':' + segs["passwd"]

            # Output .part
            if self.is_mode_input() is not True:
                try:
                    self.kvc = KaresansuiVirtConnectionAuth(uri,creds)
                    host = MergeHost(self.kvc, model)
                    for guest in host.guests:

                        _virt = self.kvc.search_kvg_guests(guest.info["model"].name)
                        if 0 < len(_virt):
                            for _v in _virt:
                                uuid = _v.get_info()["uuid"]
                                uri_guests_info[uuid] = guest.info
                                uri_guests_kvg[uuid] = _v
                                uri_guests_name[uuid] = guest.info["model"].name.encode("utf8")

                    for name in sorted(uri_guests_name.values(),key=str.lower):
                        for uuid in dict_search(name,uri_guests_name):
                            uri_guests.append(MergeGuest(uri_guests_info[uuid]["model"], uri_guests_kvg[uuid]))
                            uri_guests_status[uuid]  = uri_guests_info[uuid]['virt'].status()

                finally:
                    self.kvc.close()

                # .json
                if self.is_json() is True:
                    guests_json = []
                    for x in uri_guests:
                        guests_json.append(x.get_json(self.me.languages))

                    self.view.uri_guests = json_dumps(guests_json)
                else:
                    self.view.uri_guests = uri_guests
                    self.view.uri_guests_status = uri_guests_status

        self.kvc = KaresansuiVirtConnection()
        try: # libvirt connection scope -->

            # Storage Pool
            #inactive_pool = self.kvc.list_inactive_storage_pool()
            inactive_pool = []
            active_pool = self.kvc.list_active_storage_pool()
            pools = inactive_pool + active_pool
            pools.sort()

            if not pools:
                return web.badrequest('One can not start a storage pool.')

            # Output .input
            if self.is_mode_input() is True:
                self.view.pools = pools
                pools_info = {}
                pools_vols_info = {}
                pools_iscsi_blocks = {}
                already_vols = []
                guests = []

                guests += self.kvc.list_inactive_guest()
                guests += self.kvc.list_active_guest()
                for guest in guests:
                    already_vol = self.kvc.get_storage_volume_bydomain(domain=guest,
                                                                       image_type=None,
                                                                       attr='path')
                    if already_vol:
                        already_vols += already_vol.keys()

                for pool in pools:
                    pool_obj = self.kvc.search_kvn_storage_pools(pool)[0]
                    if pool_obj.is_active() is True:
                        pools_info[pool] = pool_obj.get_info()

                        blocks = None
                        if pools_info[pool]['type'] == 'iscsi':
                            blocks = self.kvc.get_storage_volume_iscsi_block_bypool(pool)
                            if blocks:
                                pools_iscsi_blocks[pool] = []
                        vols_obj = pool_obj.search_kvn_storage_volumes(self.kvc)
                        vols_info = {}

                        for vol_obj in vols_obj:
                            vol_name = vol_obj.get_storage_volume_name()
                            vols_info[vol_name] = vol_obj.get_info()
                            if blocks:
                                if vol_name in blocks and vol_name not in already_vols:
                                    pools_iscsi_blocks[pool].append(vol_obj.get_info())

                        pools_vols_info[pool] = vols_info

                self.view.pools_info = pools_info
                self.view.pools_vols_info = pools_vols_info
                self.view.pools_iscsi_blocks = pools_iscsi_blocks

                bridge_prefix = {
                    "XEN":"xenbr",
                    "KVM":KVM_BRIDGE_PREFIX,
                    }
                self.view.host_id = host_id
                self.view.DEFAULT_KEYMAP = DEFAULT_KEYMAP
                self.view.DISK_NON_QEMU_FORMAT = DISK_NON_QEMU_FORMAT
                self.view.DISK_QEMU_FORMAT = DISK_QEMU_FORMAT

                self.view.hypervisors = {}
                self.view.mac_address = {}
                self.view.keymaps = {}
                self.view.phydev = {}
                self.view.virnet = {}

                used_ports = {}

                for k,v in MACHINE_HYPERVISOR.iteritems():
                    if k in available_virt_mechs():
                        self.view.hypervisors[k] = v
                        uri = uris[k]
                        mem_info = self.kvc.get_mem_info()
                        active_networks = self.kvc.list_active_network()
                        used_graphics_ports = self.kvc.list_used_graphics_port()
                        bus_types = self.kvc.bus_types
                        self.view.bus_types = bus_types
                        self.view.max_mem = mem_info['host_max_mem']
                        self.view.free_mem = mem_info['host_free_mem']
                        self.view.alloc_mem = mem_info['guest_alloc_mem']

                        self.view.mac_address[k] = generate_mac_address(k)
                        self.view.keymaps[k] = eval("get_keymaps(%s_KEYMAP_DIR)" % k)

                        # Physical device
                        phydev = []
                        phydev_regex = re.compile(r"%s" % bridge_prefix[k])
                        for dev,dev_info in get_ifconfig_info().iteritems():
                            try:
                                if phydev_regex.match(dev):
                                    phydev.append(dev)
                            except:
                                pass
                        if len(phydev) == 0:
                            phydev.append("%s0" % bridge_prefix[k])
                        phydev.sort()
                        self.view.phydev[k] = phydev # Physical device

                        # Virtual device
                        self.view.virnet[k] = sorted(active_networks)
                        used_ports[k] = used_graphics_ports


                exclude_ports = []
                for k, _used_port in used_ports.iteritems():
                    exclude_ports = exclude_ports + _used_port
                    exclude_ports = sorted(exclude_ports)
                    exclude_ports = [p for p, q in zip(exclude_ports, exclude_ports[1:] + [None]) if p != q]
                self.view.graphics_port = next_number(GRAPHICS_PORT_MIN_NUMBER,
                                                 PORT_MAX_NUMBER,
                                                 exclude_ports)

            else: # .part
                models = findbyhost1guestall(self.orm, host_id)
                guests = []
                if models:
                    # Physical Guest Info
                    self.view.hypervisors = {}
                    for model in models:
                        for k,v in MACHINE_HYPERVISOR.iteritems():
                            if k in available_virt_mechs():
                                self.view.hypervisors[k] = v
                                uri = uris[k]
                                if hasattr(self, "kvc") is not True:
                                    self.kvc = KaresansuiVirtConnection(uri)
                                domname = self.kvc.uuid_to_domname(model.uniq_key)
                                #if not domname: return web.conflict(web.ctx.path)
                                _virt = self.kvc.search_kvg_guests(domname)
                                if 0 < len(_virt):
                                    guests.append(MergeGuest(model, _virt[0]))
                                else:
                                    guests.append(MergeGuest(model, None))

                # Exported Guest Info
                exports = {}
                for pool_name in pools:
                    files = []

                    pool = self.kvc.search_kvn_storage_pools(pool_name)
                    path = pool[0].get_info()["target"]["path"]

                    if os.path.exists(path):
                        for _afile in glob.glob("%s/*/info.dat" % (path,)):
                            param = ExportConfigParam()
                            param.load_xml_config(_afile)

                            _dir = os.path.dirname(_afile)

                            uuid = param.get_uuid()
                            name = param.get_domain()
                            created = param.get_created()
                            title = param.get_title()
                            if title != "":
                                title = re.sub("[\r\n]","",title)
                            if title == "":
                                title = _('untitled')

                            if created != "":
                                created_str = time.strftime("%Y/%m/%d %H:%M:%S", \
                                                            time.localtime(float(created)))
                            else:
                                created_str = _("N/A")

                            files.append({"dir": _dir,
                                          "pool" : pool_name,
                                          #"b64dir" : base64_encode(_dir),
                                          "uuid" : uuid,
                                          "name" : name,
                                          "created" : int(created),
                                          "created_str" : created_str,
                                          "title" : title,
                                          "icon" : param.get_database()["icon"],
                                          })

                    exports[pool_name] = files

                # .json
                if self.is_json() is True:
                    guests_json = []
                    for x in guests:
                        guests_json.append(x.get_json(self.me.languages))

                    self.view.guests = json_dumps(guests_json)
                else:
                    self.view.exports = exports
                    self.view.guests = guests

            return True
        except:
            pass
        finally:
            #self.kvc.close()
            pass # libvirt connection scope --> Guest#_post()

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        model = findbyhost1(self.orm, host_id)
        if model.attribute == 0 and model.hypervisor == MACHINE_HYPERVISOR["XEN"]:
            uri = uris["XEN"]
        elif model.attribute == 0 and model.hypervisor == MACHINE_HYPERVISOR["KVM"]:
            uri = uris["KVM"]
        else:
            uri = None

        if not validates_guest_add(self):
            return web.badrequest(self.view.alert)

        try:
            try:
                self.kvc = KaresansuiVirtConnection(uri)
                active_guests = self.kvc.list_active_guest()
                inactive_guests = self.kvc.list_inactive_guest()
                used_graphics_ports = self.kvc.list_used_graphics_port()
                used_mac_addrs = self.kvc.list_used_mac_addr()
                mem_info = self.kvc.get_mem_info()

                if is_param(self.input, "vm_mem_size"):
                    if mem_info['host_free_mem'] < int(self.input.vm_mem_size):
                        return web.badrequest(_("Space not enough to allocate guest memory."))

                if is_param(self.input, "pool_type") and \
                       self.input.pool_type != "block" and \
                       is_param(self.input, "pool_dir"):
                    target_path = self.kvc.get_storage_pool_targetpath(self.input.pool_dir)
                    if target_path: # disk
                        if not chk_create_disk(target_path, self.input.vm_disk_size):
                            partition = get_partition_info(target_path, header=False)
                            return web.badrequest(_("No space available to create disk image in '%s' partition.") % partition[5][0])
            except:
                raise
        finally:
            del self.kvc

        # Check on whether value has already been used
        # Guest OS
        if (self.input.domain_name in active_guests) \
               or (self.input.domain_name in inactive_guests):
            return web.conflict(web.ctx.path, "Guest OS is already there.")
        # Graphics Port Number
        if(int(self.input.vm_graphics_port) in used_graphics_ports):
            return web.conflict(web.ctx.path, "Graphics Port is already there.")
        # MAC Address
        if(self.input.vm_mac in used_mac_addrs):
            return web.conflict(web.ctx.path, "MAC Address is already there.")

        uuid = string_from_uuid(generate_uuid())

        options = {}
        options['uuid'] = uuid

        if is_param(self.input, "domain_name"):
            options['name'] = self.input.domain_name
        if is_param(self.input, "vm_mem_size"):
            options['mem-size'] = self.input.vm_mem_size
        if is_param(self.input, "vm_kernel"):
            options['kernel'] = self.input.vm_kernel
        if is_param(self.input, "vm_initrd"):
            options['initrd'] = self.input.vm_initrd
        if is_param(self.input, "vm_iso"):
            options['iso'] = self.input.vm_iso
        if is_param(self.input, "keymap"):
            options['keymap'] = self.input.keymap

        is_create = False
        if is_param(self.input, "pool_type"):
            if is_param(self.input, "bus_type"):
                options['bus'] = self.input.bus_type

            if self.input.pool_type == "dir" or self.input.pool_type == "fs": # create volume
                is_create = True
                options['disk-format'] = self.input.disk_format
                options["storage-pool"] = self.input.pool_dir
                options["storage-volume"] = options['name'] # default domain name
                options['disk-size'] = self.input.vm_disk_size

            elif self.input.pool_type == "block": # iscsi block device
                (iscsi_pool, iscsi_volume) = self.input.pool_dir.split("/", 2)
                options["storage-pool"] = iscsi_pool
                options["storage-volume"] = iscsi_volume
            else:
                return web.badrequest()
        else:
            return web.badrequest()

        if is_param(self.input, "vm_graphics_port"):
            options['graphics-port'] = self.input.vm_graphics_port
        if is_param(self.input, "vm_mac"):
            options['mac'] = self.input.vm_mac
        if is_param(self.input, "vm_extra"):
            options['extra'] = self.input.vm_extra
        if is_param(self.input, "nic_type"):
            if self.input.nic_type == "phydev":
                options['interface-format'] = "b:" + self.input.phydev
            elif self.input.nic_type == "virnet":
                options['interface-format'] = "n:" + self.input.virnet

        if int(self.input.m_hypervisor) == MACHINE_HYPERVISOR['XEN']:
            i_hypervisor = MACHINE_HYPERVISOR['XEN']
            options['type'] = u"XEN"
        elif int(self.input.m_hypervisor) == MACHINE_HYPERVISOR['KVM']:
            i_hypervisor = MACHINE_HYPERVISOR['KVM']
            options['type'] = u"KVM"
        else:
            return web.badrequest("This is not the hypervisor.")

        host = findbyhost1(self.orm, host_id)

        # notebook
        note_title = None
        if is_param(self.input, "note_title"):
            note_title = self.input.note_title

        note_value = None
        if is_param(self.input, "note_value"):
            note_value = self.input.note_value

        _notebook = n_new(note_title, note_value)

        # tags
        _tags = None
        if is_param(self.input, "tags"):
            _tags = []
            tag_array = comma_split(self.input.tags)
            tag_array = uniq_sort(tag_array)
            for x in tag_array:
                if t_count(self.orm, x) == 0:
                    _tags.append(t_new(x))
                else:
                    _tags.append(t_name(self.orm, x))

        # Icon
        icon_filename = None
        if is_param(self.input, "icon_filename", empty=True):
            icon_filename = self.input.icon_filename

        _guest = m_new(created_user=self.me,
                       modified_user=self.me,
                       uniq_key=uni_force(uuid),
                       name=self.input.m_name,
                       attribute=MACHINE_ATTRIBUTE['GUEST'],
                       hypervisor=i_hypervisor,
                       notebook=_notebook,
                       tags=_tags,
                       icon=icon_filename,
                       is_deleted=False,
                       parent=host,
                       )

        ret =  regist_guest(self,
                            _guest,
                            icon_filename,
                            VIRT_COMMAND_CREATE_GUEST,
                            options,
                            ('Create Guest', 'Create Guest'),
                            {"name": options['name'],
                             "pool" : options["storage-pool"],
                             "volume" : options["uuid"],
                             },
                            is_create,
                            )
        if ret is True:
            return web.accepted()
        else:
            return False

urls = (
    '/host/(\d+)/guest/?(\.part|\.json)$', Guest,
    )
