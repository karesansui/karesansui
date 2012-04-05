#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

""" 
<comment-ja>
スナップショットの生成と適用、情報取得を行う
</comment-ja>
<comment-en>
Take and revert snapshot of domain, or get stats of snapshot image.
</comment-en>

@file:   snapshot.py

@author: Taizo ITO <taizo@karesansui-project.info>

@copyright:    

"""

import os
import re
import libvirt
import libvirtmod
import logging
import glob

from StringIO import StringIO
from xml.dom.ext import PrettyPrint
from xml.dom.DOMImplementation import implementation

import karesansui
import karesansui.lib.locale

from karesansui.lib.utils import get_xml_parse        as XMLParse
from karesansui.lib.utils import get_xml_xpath        as XMLXpath
from karesansui.lib.utils import get_nums_xml_xpath   as XMLXpathNum
from karesansui.lib.utils import get_inspect_stack, preprint_r, r_chgrp, r_chmod
from karesansui.lib.const import VIRT_XML_CONFIG_DIR, VIRT_SNAPSHOT_DIR, KARESANSUI_GROUP
from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.virt.config import ConfigParam

from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection

class KaresansuiVirtSnapshotException(KaresansuiVirtException):
    pass

class KaresansuiVirtSnapshot:

    def __init__(self,uri=None,readonly=True):
        self.__prep()
        self.logger.debug(get_inspect_stack())
        try:
            self.kvc = KaresansuiVirtConnection(uri=uri, readonly=readonly)
        except:
            raise KaresansuiVirtSnapshotException(_("Cannot open '%s'") % uri)
        try:
            from libvirtmod import virDomainRevertToSnapshot
            from libvirtmod import virDomainSnapshotCreateXML
            from libvirtmod import virDomainSnapshotCurrent
            from libvirtmod import virDomainSnapshotDelete
            from libvirtmod import virDomainSnapshotGetXMLDesc
            from libvirtmod import virDomainSnapshotLookupByName
        except:
            raise KaresansuiVirtSnapshotException(_("Snapshot is not supported by this version of libvirt"))
        self.error_msg = []


    def __del__(self):
        self.finish()

    def __prep(self):
        self.logger = logging.getLogger('karesansui.virt.snapshot')

    def finish(self):
        try:
            self.kvc.close()
        except:
            pass

    def append_error_msg(self,string):
        self.error_msg.append(string)

    def reset_error_msg(self):
        self.error_msg = []

    def generateXML(self, doc):
        out = StringIO()
        PrettyPrint(doc, out)
        return out.getvalue()

    def isSupportedDomain(self,domain=None):
        retval = True

        inactives = self.kvc.list_inactive_guest()
        actives   = self.kvc.list_active_guest()

        if domain is not None:
            if domain in inactives + actives:
                guest = self.kvc.search_guests(domain)[0]

                param = ConfigParam(domain)
                param.load_xml_config(guest.XMLDesc(1))

                for info in param.disks:
                    """
                    { 'bus'        :'ide',
                      'device'     :'disk',
                      'disk_type'  :'file',
                      'driver_name':'qemu',
                      'driver_type':'qcow2',
                      'path'       :'/path/to/disk_image.img',
                      'target'     :'hda'}
                    """
                    try:
                        if info['driver_type'] == "qcow2":
                            pass
                        else:
                            self.append_error_msg(_("%s: unsupported image format %s") % (info['target'],info['driver_type']))
                            retval = False
                            #break
                    except:
                        retval = False
                        #break
            else:
                retval = False

        return retval

    def _snapshotListNames(self,domain=None):
        retval = []

        if domain is not None:
            for xml_path in glob.glob("%s/%s/*.xml" % (VIRT_SNAPSHOT_DIR,domain,)):
                retval.append(os.path.basename(xml_path)[0:-4])

        return retval

    def listNames(self,domain=None,all=False):
        retval = {}

        inactives = self.kvc.list_inactive_guest()
        actives   = self.kvc.list_active_guest()

        if domain is None:
            for domname in inactives + actives:
                if all is True:
                    names = self._snapshotListNames(domname)
                else:
                    guest = self.kvc.search_guests(domname)[0]
                    names = guest.snapshotListNames(0)
                retval[domname] = names
        else:
            if domain in inactives + actives:
                if all is True:
                    names = self._snapshotListNames(domain)
                else:
                    guest = self.kvc.search_guests(domain)[0]
                    names = guest.snapshotListNames(0)
                retval[domain] = names
            else:
                pass

        return retval

    def listNum(self,domain=None,all=False):
        retval = 0

        inactives = self.kvc.list_inactive_guest()
        actives   = self.kvc.list_active_guest()

        if domain is not None:
            if domain in inactives + actives:
                if all is True:
                    names = self._snapshotListNames(domain)
                    retval = len(names)
                else:
                    guest = self.kvc.search_guests(domain)[0]
                    retval = guest.snapshotNum(0)
            else:
                pass

        return retval

    def whichDomain(self,name):
        retval = []

        try:
            for domain,names in self.listNames().iteritems():
                if name in names:
                    retval.append(domain)
        except:
            pass

        return retval

    def lookupByName(self,name,domain=None):
        retval = False

        if domain is None:
            domains = self.whichDomain(name)
            if len(domains) != 0:
                domain = domains[0]

        if domain is not None:
            guest = self.kvc.search_guests(domain)[0]
            retval = libvirtmod.virDomainSnapshotLookupByName(guest._o, name, 0)

        return retval

    """
    # 親スナップショットなし
    <domainsnapshot>
      <name>1271408851</name>
      <state>running</state>
      <creationTime>1271408851</creationTime>
      <domain>
        <uuid>7833e0a3-f45e-0528-3745-f5d60bf31bd5</uuid>
      </domain>
    </domainsnapshot>

    # 親スナップショットあり
    <domainsnapshot>
      <name>1271409890</name>
      <state>running</state>
      <parent>
        <name>1271408851</name>
      </parent>
      <creationTime>1271409890</creationTime>
      <domain>
        <uuid>7833e0a3-f45e-0528-3745-f5d60bf31bd5</uuid>
      </domain>
    </domainsnapshot>
    """
    def getXMLDesc(self,name,domain=None,flag=True):
        retval = None

        snapshot = self.lookupByName(name,domain=domain)
        if snapshot is not False:

            if flag is True:
                xml_path = self.getSnapshotXMLPath(name,domain=domain)
                if os.path.exists(xml_path):
                    retval = open(xml_path).read()

            if retval is None:
                retval = libvirtmod.virDomainSnapshotGetXMLDesc(snapshot, 0)
                if retval is False:
                    retval = None

        return retval

    def getSnapshotXMLPath(self,name,domain=None):
        retval = None

        try:
            if domain is None:
                domains = self.whichDomain(name)
                if len(domains) != 0:
                    domain = domains[0]

            xml_path = "%s/%s/%s.xml" % (VIRT_SNAPSHOT_DIR,domain,name,)
            if os.path.exists(xml_path):
                retval = xml_path
        except:
            pass

        return retval

    def getSnapshotInfo(self,name,domain=None):
        retval = {}

        xml = self.getXMLDesc(name,domain=domain)
        if xml is not None:

            doc = XMLParse(xml)
            name         = XMLXpath(doc, '/domainsnapshot/name/text()')
            state        = XMLXpath(doc, '/domainsnapshot/state/text()')
            parent_name  = XMLXpath(doc, '/domainsnapshot/parent/name/text()')
            creationTime = XMLXpath(doc, '/domainsnapshot/creationTime/text()')
            domain_uuid  = XMLXpath(doc, '/domainsnapshot/domain/uuid/text()')

            retval['name']         = name
            retval['state']        = state
            retval['parent_name']  = parent_name
            retval['creationTime'] = creationTime
            retval['domain_uuid']  = domain_uuid
            if domain_uuid is not None:
                for guests in self.kvc.search_guests():
                    if domain_uuid == guests.UUIDString():
                        retval['domain_name']  = guests.name()
            try:
                retval['domain_name']
            except:
                domains  = self.whichDomain(name)
                if len(domains) != 0:
                    retval['domain_name']  = domains[0]

        return retval

    def getParentName(self,name,domain=None):
        retval = None

        info = self.getSnapshotInfo(name,domain=domain)
        if info is not False:
            try:
               retval = info['parent_name']
            except:
               pass

        return retval

    def getChildrenNames(self,name,domain=None):
        retval = []

        names = self.listNames()
        try:
            for _domain,_names in names.iteritems():
                for _name in _names:
                    if domain == _domain and _name != name and self.getParentName(_name,domain=_domain) == name:
                        retval.append(_name)
        except:
            pass

        return retval

    def hasCurrentSnapshot(self,domain=None):
        retval = False

        inactives = self.kvc.list_inactive_guest()
        actives   = self.kvc.list_active_guest()

        if domain is not None:
            if domain in inactives + actives:
                guest = self.kvc.search_guests(domain)[0]
                ret = guest.hasCurrentSnapshot(0)
                if ret != 0:
                    retval = True
            else:
                pass

        return retval


    def getCurrentSnapshotXMLDesc(self,domain=None):
        retval = False

        if domain is not None:
            has_current = self.hasCurrentSnapshot(domain)
            if has_current is True:
                guest = self.kvc.search_guests(domain)[0]
                snapshot = libvirtmod.virDomainSnapshotCurrent(guest._o,0)
                if snapshot is not False:
                    retval = libvirtmod.virDomainSnapshotGetXMLDesc(snapshot, 0)

        return retval

    def getCurrentSnapshotName(self,domain=None,force=True):
        retval = False

        if domain is not None:
            xml = self.getCurrentSnapshotXMLDesc(domain)
            if xml is not False:
                doc = XMLParse(xml)
                retval = XMLXpath(doc, '/domainsnapshot/name/text()')

            # 取得できなければ、domainのXMLファイルから取得
            else:
                if force is True:
                    xml_path = "%s/%s.xml" %(VIRT_XML_CONFIG_DIR,domain,)
                    if os.path.exists(xml_path):
                        try:
                            doc = XMLParse(xml_path)
                            retval = XMLXpath(doc, '/domain/currentSnapshot/text()')
                        except:
                            pass

        return retval

    def getCurrentSnapshotInfo(self,domain=None):
        retval = False

        if domain is not None:
            name = self.getCurrentSnapshotName(domain)
            if name is not False:
                retval = self.getSnapshotInfo(name,domain=domain)

        return retval

    def createSnapshot(self, domain=None, xmlDesc=None):
        retval = False

        if domain is not None:
            parent_snapshot_name = self.getCurrentSnapshotName(domain)

            if xmlDesc is None:
                xml = "<domainsnapshot/>"

            else: # validate xml file
                try:
                    doc = XMLParse(xmlDesc)
                    name = XMLXpath(doc, '/domainsnapshot/name/text()')
                    if name is not None:
                        xml = xmlDesc
                except:
                    pass
            try:
                xml
                guest = self.kvc.search_guests(domain)[0]
                snapshot = libvirtmod.virDomainSnapshotCreateXML(guest._o,xml,0)
                if snapshot is not False:
                    retval = libvirtmod.virDomainSnapshotGetXMLDesc(snapshot, 0)
            except:
                pass

        if retval is not False:
            kvg_guest = self.kvc.search_kvg_guests(domain)[0]
            id = self.getCurrentSnapshotName(domain)
            kvg_guest.set_current_snapshot(id)

            # ここにsnapshotのxmlファイルに親のsnapshotの情報を書き込む処理
            try:
                xml_path = self.getSnapshotXMLPath(id)

                # <parent/>が設定されてない場合
                # かつ、snapshot実行前に<currentSnapshot/>が設定されていた場合
                if self.getParentName(id) is None and parent_snapshot_name is not None:
                    if os.path.exists(xml_path):
                        doc = XMLParse(xml_path)
                        parent = doc.createElement("parent")
                        name   = doc.createElement("name")
                        txt = doc.createTextNode(str(parent_snapshot_name))
                        name.appendChild(txt)
                        parent.appendChild(name)
                        doc.childNodes[0].appendChild(parent)
                        xmlDesc = self.generateXML(doc)

                        ConfigFile(xml_path).write(xmlDesc)

                if os.path.exists(xml_path):
                    if os.getuid() == 0:
                        r_chgrp(xml_path,KARESANSUI_GROUP)
                        r_chmod(xml_path,"g+rw")
                        r_chmod(xml_path,"o-rwx")
            except:
                pass

        return retval

    def deleteSnapshot(self, name, domain=None):
        retval = False

        snapshot = self.lookupByName(name,domain=domain)
        if snapshot is not False:

            if domain is None:
                domains = self.whichDomain(name)
                if len(domains) != 0:
                    domain = domains[0]

            retval = libvirtmod.virDomainSnapshotDelete(snapshot, 0)

        if retval is not False:
            kvg_guest = self.kvc.search_kvg_guests(domain)[0]
            id = self.getCurrentSnapshotName(domain)
            kvg_guest.set_current_snapshot(id)

        return retval

    def revertSnapshot(self, name, domain=None):
        retval = False

        snapshot = self.lookupByName(name,domain=domain)
        if snapshot is not False:

            if domain is None:
                domains = self.whichDomain(name)
                if len(domains) != 0:
                    domain = domains[0]

            kvg_guest = self.kvc.search_kvg_guests(domain)[0]

            guest = kvg_guest._conn.lookupByName(domain)
            retval = libvirtmod.virDomainRevertToSnapshot(guest,snapshot, 0)

        if retval is not False:
            id = self.getCurrentSnapshotName(domain)
            kvg_guest.set_current_snapshot(id)

        return retval

    def refreshSnapshot(self):
        from karesansui.lib.utils import execute_command

        inactives = self.kvc.list_inactive_guest()
        actives   = self.kvc.list_active_guest()

        do_refresh = False
        for domname in inactives + actives:
            all_num    = self.listNum(domain=domname,all=True)
            active_num = self.listNum(domain=domname,all=False)
            if all_num > 0 and active_num == 0:
                do_refresh = True

        # 差分があれば実行
        if do_refresh is True:
            command = "/etc/init.d/libvirtd restart"
            command_args = command.split(" ")
            (rc,res) = execute_command(command_args)
            pass

        return True

if __name__ == '__main__':
    """Testing
    """

    kvs = KaresansuiVirtSnapshot()

    """
    names = kvs.listNames()

    for _k,_v in names.iteritems():
        for _k2 in _v:
            print kvs.whichDomain(_k2)
            print kvs.lookupByName(_k2)
            print kvs.getXMLDesc(_k2)
            preprint_r(kvs.getSnapshotInfo(_k2))

        has_current = kvs.hasCurrentSnapshot(_k)
        if has_current is False:
            print "domain %s does not have current snapshot." % (_k,)
        else:
            print "domain %s has current snapshot." % (_k,)
            print kvs.getCurrentSnapshotXMLDesc(_k)
            preprint_r(kvs.getCurrentSnapshotInfo(_k))

    #print "createSnapshot"
    #print kvs.createSnapshot('guest1')
    #print kvs.revertSnapshot('1271409890')
    print kvs.isSupportedDomain('guest1')
    print kvs.isSupportedDomain('guest2')

    print kvs.getParentName('1271409890')
    print kvs.getChildrenNames('1271409890')

    print kvs.getCurrentSnapshotName("guest2")
    xml_path = kvs.getSnapshotXMLPath("1274174139")
    if os.path.exists(xml_path):
        dom = XMLParse(xml_path)
        parent = dom.createElement("parent")
        name   = dom.createElement("name")
        txt = dom.createTextNode("hoge")
        name.appendChild(txt)
        parent.appendChild(name)
        dom.childNodes[0].appendChild(parent)
        xmlDesc = kvs.generateXML(dom)
        print xmlDesc

    id = u'1274235845'
    print kvs.getSnapshotXMLPath(id)
    print kvs.getXMLDesc(id)

    id = '1274235848'
    id = '1274235841'
    for domain in kvs.whichDomain(id):
        print kvs.getSnapshotXMLPath(id,domain=domain)
        print kvs.getXMLDesc(id,domain=domain)
        print kvs.getChildrenNames(id,domain=domain)
    """

    names = kvs.listNames()
    preprint_r(names)
    names = kvs.listNames(all=True)
    preprint_r(names)

    kvs.refreshSnapshot()

    kvs.finish()
