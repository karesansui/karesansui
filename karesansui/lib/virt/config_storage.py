#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
""" 
<comment-ja>
libvirtのStorage Pool/Volume の設定を生成する
</comment-ja>
<comment-en>
Generate configuration file of storage pool/volume for libvirt.
</comment-en>

@file:   config_storage.py

@author: Kei Funagayama <kei@karesansui-project.info>
"""

import time
import os, stat
import re
from StringIO import StringIO
from xml.dom.ext import PrettyPrint
from xml.dom.DOMImplementation import implementation
import errno

import karesansui
from karesansui.lib.const import KARESANSUI_GROUP, \
     VIRT_STORAGE_CONFIG_DIR
from karesansui.lib.utils import get_xml_parse        as XMLParse
from karesansui.lib.utils import get_xml_xpath        as XMLXpath
from karesansui.lib.utils import r_chgrp, r_chmod, symlink2real
from karesansui.lib.file.configfile import ConfigFile

class KaresansuiStorageConfigParamException(karesansui.KaresansuiLibException):
    pass

class KaresansuiStoragePoolConfigParamException(KaresansuiStorageConfigParamException):
    pass

class KaresansuiStorageVolumeConfigParamException(KaresansuiStorageConfigParamException):
    pass


class StorageConfigParam:
    def set_uuid(self, uuid):
        self.uuid = uuid
    def get_uuid(self):
        return self.uuid

    def set_allocation(self, allocation):
        self.allocation = allocation
    def get_allocation(self):
        return self.allocation

    def set_capacity(self, capacity):
        self.capacity = capacity
    def get_capacity(self):
        return self.capacity

    def set_storage_name(self, name):
        self.name = name
    def get_storage_name(self):
        return self.name

class StoragePoolConfigParam(StorageConfigParam):

    def __init__(self, arg):
        if isinstance(arg, basestring):
            # expect name as string
            self.name = arg
            self.uuid = None
            self.p_type = None
            self.allocation = None
            self.capacity = None
            self.available = None
            self.s_dev_path = None
            self.s_dir_path = None
            self.s_h_name = None
            #self.s_name = None
            self.s_f_type = None
            self.t_path = None
            self.t_p_owner = None
            self.t_p_group = None
            self.t_p_mode = None
            self.t_p_label = None
            self.t_e_format = None
            self.t_e_s_type = None
            self.t_e_s_uuid = None

        else:
            self.name = arg['name']
            self.uuid = arg['uuid']
            self.p_type = arg['pool']['type']
            self.allocation = arg['allocation']
            self.capacity = arg['capacity']
            self.available = arg['available']
            self.s_dev_path = arg['source']['device']['path']
            self.s_dir_path = arg['source']['directory']['path']
            self.s_h_name = arg['source']['host']['name']
            #self.s_name = arg['source']['name']
            self.s_f_type = arg['source']['format']['type']
            self.t_path = arg['target']['path']
            self.t_p_owner = arg['target']['permissions']['owner']
            self.t_p_group = arg['target']['permissions']['group']
            self.t_p_mode = arg['target']['permissions']['mode']
            self.t_p_label = arg['target']['permissions']['label']
            self.t_e_format = arg['target']['encryption']['format']
            self.t_e_s_type = arg['target']['encryption']['secret']['type']
            self.t_e_s_uuid = arg['target']['encryption']['secret']['uuid']

    def set_pool_type(self, p_type):
        self.p_type = p_type
    def get_pool_type(self):
        return self.p_type

    def set_available(self, available):
        self.available = available
    def get_available(self):
        return self.available

    def set_source_dev_path(self, s_dev_path):
        self.s_dev_path = s_dev_path
    def get_source_dev_path(self):
        return self.s_dev_path

    def set_source_dir_path(self, s_dir_path):
        self.s_dir_path = s_dir_path
    def get_source_dir_path(self):
        return self.s_dir_path

    def set_source_h_name(self, s_h_name):
        self.s_h_name = s_h_name
    def get_source_h_name(self):
        return self.s_h_name

    def set_source_f_type(self, s_f_type):
        self.s_f_type = s_f_type
    def get_source_f_type(self):
        return self.s_f_type

    def set_target_path(self, t_path):
        self.t_path = t_path
    def get_target_path(self):
        return self.t_path

    def set_target_permissions_owner(self, t_p_owner):
        self.t_p_owner = t_p_owner
    def get_target_permissions_owner(self):
        return self.t_p_owner

    def set_target_permissions_group(self, t_p_group):
        self.t_p_group = t_p_group
    def get_target_permissions_group(self):
        return self.t_p_group

    def set_target_permissions_mode(self, t_p_mode):
        self.t_p_mode = t_p_mode
    def get_target_permissions_mode(self):
        return self.t_p_mode

    def set_target_permissions_label(self, t_p_label):
        self.t_p_label = t_p_label
    def get_target_permissions_label(self):
        return self.t_p_label

    def set_target_e_format(self, t_e_format):
        self.t_e_format = t_e_format
    def get_target_e_format(self):
        return self.t_e_format

    def set_target_encryption_s_type(self, t_e_s_type):
        self.t_e_s_type = t_e_s_type
    def get_target_encryption_s_type(self):
        return self.t_e_s_type

    def set_target_encryption_s_uuid(self, t_e_s_uuid):
        self.t_e_s_uuid = t_e_s_uuid
    def get_target_encryption_s_uuid(self):
        return self.t_e_s_uuid

    def load_xml_config(self,path):
        document = XMLParse(path)

        p_type =  XMLXpath(document, '/pool/@type')        
        self.set_pool_type(p_type)

        uuid = XMLXpath(document,'/pool/uuid/text()')
        self.set_uuid(str(uuid))

        allocation = XMLXpath(document, '/pool/allocation/text()')
        self.set_allocation(allocation)

        capacity = XMLXpath(document, '/pool/capacity/text()')
        self.set_capacity(capacity)

        available = XMLXpath(document, '/pool/available/text()')
        self.set_available(available)

        s_dev_path = XMLXpath(document, '/pool/source/device/@path')
        self.set_source_dev_path(s_dev_path)

        s_dir_path = XMLXpath(document, '/pool/source/directory/@path')
        self.set_source_dir_path(s_dir_path)

        s_h_name = XMLXpath(document, '/pool/source/host/@name')
        self.set_source_h_name(s_h_name)

        s_f_type = XMLXpath(document, '/pool/source/format/@type')
        self.set_source_f_type


        t_path = XMLXpath(document, '/pool/target/path/text()')
        self.set_target_path(t_path)

        t_p_owner = XMLXpath(document, '/pool/target/permissions/owner/text()')
        self.set_target_permissions_owner(t_p_owner)
        
        t_p_group = XMLXpath(document, '/pool/target/permissions/group/text()')
        self.set_target_permissions_group(t_p_group)

        t_p_mode = XMLXpath(document, '/pool/target/permissions/mode/text()')
        self.set_target_permissions_mode(t_p_mode)

        t_p_label = XMLXpath(document, '/pool/target/permissions/label/text()')
        self.set_target_permissions_label(t_p_label)

        t_e_format = XMLXpath(document, '/pool/target/encryption/@format')
        self.set_target_e_format(t_e_format)

        t_e_s_type = XMLXpath(document, '/pool/target/encryption/secret/@type')
        self.set_target_encryption_s_type(t_e_s_type)

        t_e_s_uuid = XMLXpath(document, '/pool/target/encryption/secret/@uuid')
        self.set_target_encryption_s_uuid(t_e_format)

    def validate(self):

        if not self.uuid:
            raise KaresansuiStorageConfigParamException("ConfigParam: uuid is None")
        if not self.name or not len(self.name):
            raise KaresansuiStorageConfigParamException("ConfigParam: illegal name")


#--
class StorageVolumeConfigParam(StorageConfigParam):

    def __init__(self, arg):
        if isinstance(arg, basestring):
            # expect name as string
            self.name = arg
            self.uuid = None
            self.key = None
            self.allocation = None
            self.capacity = None
            self.c_unit = None
            self.source = None

            self.t_path = None
            self.t_f_type = None
            self.t_p_owner = None
            self.t_p_group = None
            self.t_p_mode = None
            self.t_p_label = None

            self.b_path = None
            self.b_format = None
            self.b_p_owner = None
            self.b_p_group = None
            self.b_p_mode = None
            self.b_p_label = None

        else:
            # expect dict in KaresansuiVirtStorageVolume#get_info() format
            self.name = arg['name']
            self.uuid = arg['uuid']
            
            self.key = arg['key']
            self.allocation = arg['allocation']
            self.capacity = arg['capacity']
            self.c_unit = arg['capacity']['unit']
            self.source = arg['source']
            
            self.t_path = arg['target']['path']
            self.t_f_type = arg['target']['format']['type']
            self.t_p_owner = arg['target']['permissions']['owner']
            self.t_p_group = arg['target']['permissions']['group']
            self.t_p_mode = arg['target']['permissions']['mode']
            self.t_p_label = arg['target']['permissions']['label']

            self.b_path = arg['backingStore']['path']
            self.b_format = arg['backingStore']['format']
            self.b_p_owner = arg['backingStore']['permissions']['owner']
            self.b_p_group = arg['backingStore']['permissions']['group']
            self.b_p_mode = arg['backingStore']['permissions']['mode']
            self.b_p_label = arg['backingStore']['permissions']['label']

    def set_key(self, key):
        self.key = key
    def get_key(self):
        return self.key

    def set_c_unit(self, c_unit):
        self.c_unit = c_unit
    def get_c_unit(self):
        return self.c_unit

    def set_source(self, source):
        self.source = source
    def get_source(self):
        return self.source

    def set_target_path(self, t_path):
        self.t_path = t_path
    def get_target_path(self):
        return self.t_path

    def set_target_f_type(self, t_f_type):
        self.t_f_type = t_f_type
    def get_target_f_type(self):
        return self.t_f_type

    def set_target_permissions_owner(self, t_p_owner):
        self.t_p_owner = t_p_owner
    def get_target_permissions_owner(self):
        return self.t_p_owner

    def set_target_permissions_group(self, t_p_group):
        self.t_p_group = t_p_group
    def get_target_permissions_group(self):
        return self.t_p_group

    def set_target_permissions_mode(self, t_p_mode):
        self.t_p_mode = t_p_mode
    def get_target_permissions_mode(self):
        return self.t_p_mode

    def set_target_permissions_label(self, t_p_label):
        self.t_p_label = t_p_label
    def get_target_permissions_label(self):
        return self.t_p_label

    def set_backingStore_path(self, b_path):
        self.b_path = b_path
    def get_backingStore_path(self):
        return self.b_path

    def set_backingStore_format(self, b_format):
        self.b_format = b_format
    def get_backingStore_format(self):
        return self.b_format

    def set_backingStore_permissions_owner(self, b_p_owner):
        self.b_p_owner = b_p_owner
    def get_backingStore_permissions_owner(self):
        return self.b_p_owner

    def set_backingStore_permissions_group(self, b_p_group):
        self.b_p_group = b_p_group
    def get_backingStore_permissions_group(self):
        return self.b_p_group

    def set_backingStore_permissions_mode(self, b_p_mode):
        self.b_p_mode = b_p_mode
    def get_backingStore_permissions_mode(self):
        return self.b_p_mode

    def set_backingStore_permissions_label(self, b_p_label):
        self.b_p_label = b_p_label
    def get_backingStore_permissions_label(self):
        return self.b_p_label

    def get_symlink2real(self):
        return symlink2real(self.get_target_path())
        
    def load_xml_config(self,path):
        document = XMLParse(path)

        name = XMLXpath(document,'/volume/name/text()')
        self.set_storage_name(str(name))

        uuid = XMLXpath(document,'/volume/uuid/text()')
        self.set_uuid(str(uuid))

        key = XMLXpath(document, '/volume/key/text()')
        self.set_key(key)

        allocation = XMLXpath(document, '/volume/allocation/text()')
        self.set_allocation(allocation)

        capacity = XMLXpath(document, '/volume/capacity/text()')
        self.set_capacity(capacity)

        c_unit = XMLXpath(document, '/volume/source/@unit')
        self.set_c_unit(c_unit)

        source = XMLXpath(document, '/volume/source/text()')
        self.set_source(source)
  
        t_path = XMLXpath(document, '/volume/target/path/text()')
        self.set_target_path(t_path)

        t_f_type = XMLXpath(document, '/volume/target/format/@type')
        self.set_target_f_type(t_f_type)

        t_p_owner = XMLXpath(document, '/volume/target/permissions/owner/text()')
        self.set_target_permissions_owner(t_p_owner)

        t_p_group = XMLXpath(document, '/volume/target/permissions/group/text()')
        self.set_target_permissions_group(t_p_group)

        t_p_mode = XMLXpath(document, '/volume/target/permissions/mode/text()')
        self.set_target_permissions_mode(t_p_mode)

        t_p_label = XMLXpath(document, '/volume/target/permissions/label/text()')
        self.set_target_permissions_label(t_p_label)

        b_path = XMLXpath(document, '/volume/backingStore/path/text()')
        self.set_backingStore_path(b_path)

        b_format = XMLXpath(document, '/volume/backingStore/format/text()')
        self.set_backingStore_format(b_format)

        b_p_owner = XMLXpath(document, '/volume/backingStore/permissions/owner/text()')
        self.set_backingStore_permissions_owner(b_p_owner)

        b_p_group = XMLXpath(document, '/volume/backingStore/permissions/group/text()')
        self.set_backingStore_permissions_group(b_p_group)

        b_p_mode = XMLXpath(document, '/volume/backingStore/permissions/mode/text()')
        self.set_backingStore_permissions_mode(b_p_mode)

        b_p_label = XMLXpath(document, '/volume/backingStore/permissions/label/text()')
        self.set_backingStore_permissions_label(b_p_label)

    def validate(self):

        if not self.uuid:
            raise KaresansuiStorageConfigParamException("ConfigParam: uuid is None")
        if not self.name or not len(self.name):
            raise KaresansuiStorageConfigParamException("ConfigParam: illegal name")

class StorageXMLGenerator:

    def __init__(self):
        self.config_dir = VIRT_STORAGE_CONFIG_DIR

    def _create_text_node(self, tag, txt):
        node = self.document.createElement(tag)
        self._add_text(node, txt)
        return node

    def _add_text(self, node, txt):
        txt_n = self.document.createTextNode(txt)
        node.appendChild(txt_n)

    def generate(self, config):
        tree = self.generate_xml_tree(config)
        out = StringIO()
        PrettyPrint(tree, out)
        return out.getvalue()

    def end_build(self):
        pass

    def writecfg(self,cfg):
        try:
            os.makedirs(self.config_dir)
        except OSError, (err, msg):
            if err != errno.EEXIST:
                raise OSError(err,msg)

        filename = "%s/%s.xml" %(self.config_dir,
                                 self.config.get_storage_name())
        ConfigFile(filename).write(cfg)
        r_chmod(filename,"o-rwx")
        r_chmod(filename,"g+rw")
        if os.getuid() == 0:
            r_chgrp(filename,KARESANSUI_GROUP)

class StoragePoolXMLConfigGenerator(StorageXMLGenerator):

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config
        self.begin_build()
        self.build_allocation()
        self.build_capacity()
        self.build_source()
        self.build_target()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.pool = self.document.createElement("pool")

        self.pool.setAttribute('type', self.config.get_pool_type())

        name = self._create_text_node("name", self.config.get_storage_name())
        uuid = self._create_text_node("uuid", self.config.get_uuid())
        self.pool.appendChild(name)
        self.pool.appendChild(uuid)

        self.document.appendChild(self.pool)

    def build_allocation(self):
        allocation = self._create_text_node("allocation",
                                        str(self.config.get_allocation()))
        self.pool.appendChild(allocation)

    def build_capacity(self):
        capacity = self._create_text_node("capacity",
                                        str(self.config.get_capacity()))
        self.pool.appendChild(capacity)

    def build_source(self):
        doc = self.document
        source = doc.createElement('source')

        if self.config.get_source_dev_path() is not None:
            device = doc.createElement('device')
            device.setAttribute('path', str(self.config.get_source_dev_path()))
            source.appendChild(device)

        if self.config.get_source_dir_path() is not None:
            directory = doc.createElement('directory')
            directory.setAttribute('path', str(self.config.get_source_dir_path()))
            source.appendChild(directory)
        
        if self.config.get_source_h_name() is not None:
            host = doc.createElement('host')
            host.setAttribute('name', str(self.config.get_source_h_name()))
            source.appendChild(host)

        if self.config.get_source_f_type() is not None:
            format = doc.createElement('format')
            format.setAttribute('type', str(self.config.get_source_f_type()))
            source.appendChild(format)

        self.pool.appendChild(source)

    def build_target(self):
        def build_permissions(self):
            doc = self.document
            permissions = doc.createElement("permissions")
            if self.config.get_target_permissions_owner() is not None:
                permissions.appendChild(
                    self._create_text_node("owner",
                                           str(self.config.get_target_permissions_owner())))
            if self.config.get_target_permissions_group() is not None:
                permissions.appendChild(
                    self._create_text_node("group",
                                           str(self.config.get_target_permissions_group())))
            if self.config.get_target_permissions_mode() is not None:
                permissions.appendChild(
                    self._create_text_node("mode",
                                           str(self.config.get_target_permissions_mode())))
            if self.config.get_target_permissions_label() is not None:
                permissions.appendChild(
                    self._create_text_node("label",
                                           str(self.config.get_target_permissions_label())))

            return permissions

        def build_encryption(self):
            doc = self.document
            encryption = doc.createElement("encryption")

            if self.config.get_target_e_format() is not None and \
                   self.config.get_target_encryption_s_type() is not None and \
                   self.config.get_target_encryption_s_uuid() is not None:

                encryption.setAttribute('format', str(self.config.get_target_e_format()))
                secret = doc.createElement("secret")
                secret.setAttribute('type', str(self.config.get_target_encryption_s_type()))
                secret.setAttribute('uuid', str(self.config.get_target_encryption_s_uuid()))
                encryption.appendChild(secret)
                
            return encryption

        doc = self.document
        target = doc.createElement("target")
        target.appendChild(self._create_text_node("path",
                                                  str(self.config.get_target_path())))
        
        target.appendChild(build_permissions(self))
        target.appendChild(build_encryption(self))

        self.pool.appendChild(target)


class StorageVolumeXMLConfigGenerator(StorageXMLGenerator):

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config

        self.begin_build()
        self.build_key()
        self.build_allocation()
        self.build_capacity()
        self.build_source()
        self.build_target()
        self.build_backingStore()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.volume = self.document.createElement("volume")

        name = self._create_text_node("name", self.config.get_storage_name())
        uuid = self._create_text_node("uuid", self.config.get_uuid())
        self.volume.appendChild(name)
        self.volume.appendChild(uuid)

        self.document.appendChild(self.volume)

    def build_key(self):
        if self.config.get_key() is not None:
            self.volume.appendChild(self._create_text_node("key",
                                                           str(self.config.get_key())))

    def build_allocation(self):
        self.volume.appendChild(self._create_text_node("allocation",
                                    str(self.config.get_allocation())))
    def build_capacity(self):
        capacity = self._create_text_node("capacity",
                                        str(self.config.get_capacity()))
        if self.config.get_c_unit() is not None:
            capacity.setAttribute("unit", str(self.config.get_c_unit()))

        self.volume.appendChild(capacity)

    def build_source(self):
        if self.config.get_source() is not None:
            self.volume.appendChild(self._create_text_node("source",
                                                           str(self.config.get_source())))

    def build_target(self):
        def build_permissions(self):
            doc = self.document
            permissions = doc.createElement("permissions")
            if self.config.get_target_permissions_owner() is not None:
                permissions.appendChild(
                    self._create_text_node("owner",
                                           str(self.config.get_target_permissions_owner())))
            if self.config.get_target_permissions_group() is not None:
                permissions.appendChild(
                    self._create_text_node("group",
                                           str(self.config.get_target_permissions_group())))
            if self.config.get_target_permissions_mode() is not None:
                permissions.appendChild(
                    self._create_text_node("mode",
                                           str(self.config.get_target_permissions_mode())))
            if self.config.get_target_permissions_label() is not None:
                permissions.appendChild(
                    self._create_text_node("label",
                                           str(self.config.get_target_permissions_label())))

            return permissions
            
        doc = self.document
        target = doc.createElement("target")
        #target.appendChild(self._create_text_node("path",
        #                                          str(self.config.get_target_path())))

        format = doc.createElement("format")
        format.setAttribute("type",
                            str(self.config.get_target_f_type()))

        target.appendChild(format)

        target.appendChild(build_permissions(self))

        self.volume.appendChild(target)

    def build_backingStore(self):
        def build_permissions(self):
            doc = self.document
            permissions = doc.createElement("permissions")
            if self.config.get_backingStore_permissions_owner() is not None:
                permissions.appendChild(
                    self._create_text_node("owner",
                                           str(self.config.get_backingStore_permissions_owner())))
            if self.config.get_backingStore_permissions_group() is not None:
                permissions.appendChild(
                    self._create_text_node("group",
                                           str(self.config.get_backingStore_permissions_group())))

            if self.config.get_backingStore_permissions_mode() is not None:
                permissions.appendChild(
                    self._create_text_node("mode",
                                           str(self.config.get_backingStore_permissions_mode())))
            if self.config.get_backingStore_permissions_label() is not None:
                permissions.appendChild(
                    self._create_text_node("label",
                                           str(self.config.get_backingStore_permissions_label())))

            return permissions
            
        if self.config.get_backingStore_path() is not None and \
               self.config.get_backingStore_format() is not None:

            doc = self.document
            backingStore = doc.createElement("backingStore")

            backingStore.appendChild(self._create_text_node("path",
                                                            str(self.config.get_backingStore_path())))
            backingStore.appendChild(self._create_text_node("format",
                                                            str(self.config.get_backingStore_format())))

            backingStore.appendChild(build_permissions(self))
            self.volume.appendChild(backingStore)
