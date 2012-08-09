#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

""" 
<comment-ja>
</comment-ja>
<comment-en>
Generate configuration file of info.dat.
</comment-en>

@file:   config_export.py

@author: Taizo ITO <taizo@karesansui-project.info>
"""

import os
import time

import errno
from StringIO import StringIO
from xml.dom.minidom import DOMImplementation
implementation = DOMImplementation()

import karesansui

from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_nums_xml_xpath as XMLXpathNum, \
     get_xml_parse as XMLParse, \
     r_chgrp, r_chmod

from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.const import VIRT_DOMAINS_DIR, KARESANSUI_GROUP


class KaresasnuiExportConfigParamException(karesansui.KaresansuiLibException):
    pass

class ExportConfigParam:

    def __init__(self, uuid=None):

        self.path      = None
        self.uuid      = uuid
        self.domain    = None
        self.title     = None
        self.created   = None
        self.database = None
        # エクスポート元のストレージプール名
        self.pool = None
        self.disks = []
        self.snapshots = None

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def get_uuid(self):
        return self.uuid

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_domain(self):
        return self.domain

    def set_domain(self, domain):
        self.domain = domain

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_created(self):
        return self.created

    def set_created(self, created):
        try:
            created = str(created)
        except:
            created = None
        self.created = created

    def get_database(self):
        return self.database

    def set_database(self, database):
        self.database = database

    def get_pool(self):
        return self.pool

    def set_pool(self, pool):
        self.pool = pool

    def get_disks(self):
        return self.disks

    def set_disks(self, disks):
        self.disks = disks

    def get_snapshots(self):
        return self.snapshots

    def set_snapshots(self, snapshots):
        self.snapshots = snapshots

    def get_default_export_dir(self, uuid):
        return "%s/%s" % (VIRT_DOMAINS_DIR,uuid,)

    def add_export(self, uuid, domain, title, database, pool, disks, created=None, snapshots=None):
        self.set_uuid(uuid)
        self.set_domain(domain)
        self.set_title(title)
        self.set_database(database)
        self.set_pool(pool)
        self.set_disks(disks)
        self.set_snapshots(snapshots)

        if created is None:
            created = str(int(time.time()))
        else:
            pass
        self.set_created(created)

        if self.path is None:
            self.set_path(self.get_default_export_dir(uuid))

    def add_disk(self, uuid, name, path):
        """<comment-ja>
        @param uuid: Storage Volume UUID
        @param name: Storage Pool Name
        @param path: Storage Pool Path
        </comment-ja>
        <comment-en>
        TODO: English Documents(en)
        </comment-en>
        """
        self.disks.append({"uuid" : uuid, "name" : name, "path" : path,})

    def add_snapshot(self, name, title, value):
        self.snapshots.append({"name":name , "title":title, "value":value,})

    def load_xml_config(self, path=None):
        if path is not None:
            self.path = path

        if not os.path.isfile(self.path):
            raise KaresasnuiExportConfigParamException(
                "File not found. path=%s" % (str(self.path)))

        document = XMLParse(self.path)

        uuid    = XMLXpath(document, '/export/@id')
        domain  = XMLXpath(document, '/export/domain/text()')
        title   = XMLXpath(document, '/export/title/text()')
        created = XMLXpath(document, '/export/created/text()')

        database = {'name' : XMLXpath(document, '/export/database/name/text()'),
                    'tags' : XMLXpath(document, '/export/database/tags/text()'),
                    'attribute' : XMLXpath(document, '/export/database/attribute/text()'),
                    'uniq_key' : XMLXpath(document, '/export/database/uniq_key/text()'),
                    'hypervisor' : XMLXpath(document, '/export/database/hypervisor/text()'),
                    'icon' : XMLXpath(document, '/export/database/icon/text()'),
                    'notebook' : {
                        'title' : XMLXpath(document, '/export/database/notebook/title/text()'),
                        'value' : XMLXpath(document, '/export/database/notebook/value/text()'),
                        },
                    }

        disks = []
        disk_num = XMLXpathNum(document,'/export/disks/disk')
        for n in range(1, disk_num + 1):
            duuid = XMLXpath(document, '/export/disks/disk[%i]/@uuid' % n)
            dname = XMLXpath(document, '/export/disks/disk[%i]/name/text()' % n)
            dpath = XMLXpath(document, '/export/disks/disk[%i]/path/text()' % n)
            disks.append({"uuid" : duuid, "name" : dname, "path" : dpath,})

        pool = XMLXpath(document, '/export/pool/text()')

        snapshots = []
        snapshot_num = XMLXpathNum(document,'/export/snapshots/snapshot')
        for n in range(1, snapshot_num + 1):
            name  = XMLXpath(document, '/export/snapshots/snapshot[%i]/@name' % n)
            title = XMLXpath(document, '/export/snapshots/snapshot[%i]/title/text()' % n)
            value = XMLXpath(document, '/export/snapshots/snapshot[%i]/value/text()' % n)
            snapshots.append({"name":name, "title":title, "value":value,})

        self.add_export(uuid, domain, title, database, pool, disks, created=created, snapshots=snapshots)

    def validate(self):
        pass

class ExportXMLGenerator:

    def __init__(self, path):
        self.path = path

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
        out.write(tree.toxml())
        return out.getvalue()

    def writecfg(self, cfg):
        ConfigFile(self.path).write(cfg)
        r_chmod(self.path, "o-rwx")
        r_chmod(self.path, "g+rw")

        if os.getuid() == 0:
            r_chgrp(self.path, KARESANSUI_GROUP)

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config
        self.begin_build()
        self.build_database()
        self.build_disks()
        self.build_snapshots()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)

        self.export = self.document.createElement("export")
        self.export.setAttribute("id", self.config.get_uuid())

        domain = self.config.get_domain()
        if domain is not None:
            n_domain = self._create_text_node("domain", domain)
            self.export.appendChild(n_domain)

        title = self.config.get_title()
        if title is not None:
            n_title = self._create_text_node("title", title)
            self.export.appendChild(n_title)

        created = self.config.get_created()
        if created is not None:
            n_created = self._create_text_node("created", created)
            self.export.appendChild(n_created)

        pool = self.config.get_pool()
        if pool is not None:
            n_pool = self._create_text_node("pool", pool)
            self.export.appendChild(n_pool)

        self.document.appendChild(self.export)

    def build_database(self):
        doc = self.document
        database = self.config.get_database()
        self.database = doc.createElement("database")

        for _k,_v in database.iteritems():
            if _v is not None:
                if type(_v) is dict:
                    child_elem = doc.createElement(_k)
                    for _n_k, _n_v in _v.iteritems():
                        child_node = self._create_text_node(_n_k, _n_v)
                        child_elem.appendChild(child_node)
                    self.database.appendChild(child_elem)
                elif type(_v) in (str, unicode):
                    node = self._create_text_node(_k, str(_v.encode('utf-8')))
                else:
                    node = self._create_text_node(_k, str(_v))
            else:
                node = doc.createElement(_k)
            self.database.appendChild(node)
        self.export.appendChild(self.database)

    def build_disks(self):
        doc = self.document
        disks = self.config.get_disks()
        self.disks = doc.createElement("disks")

        for disk in disks:
            elem_disk = doc.createElement("disk")
            # uuid
            elem_disk.setAttribute("uuid", disk['uuid'])
            # name
            elem_disk.appendChild(self._create_text_node("name", disk["name"]))
            # path
            elem_disk.appendChild(self._create_text_node("path", disk["path"]))

            self.disks.appendChild(elem_disk)

        self.export.appendChild(self.disks)

    def build_snapshots(self):
        doc = self.document
        snapshots = self.config.get_snapshots()
        if snapshots is not None:
            self.snapshots = doc.createElement("snapshots")
            for snapshot in snapshots:
                elem_snapshot = doc.createElement("snapshot")
                # name
                elem_snapshot.setAttribute("name", snapshot['name'])
                # title
                elem_snapshot.appendChild(self._create_text_node("title", snapshot["title"]))
                # value
                elem_snapshot.appendChild(self._create_text_node("value", snapshot["value"]))

                self.snapshots.appendChild(elem_snapshot)

            self.export.appendChild(self.snapshots)

    def end_build(self):
        pass

if __name__ == '__main__':
    orig_xml = """<?xml version='1.0' encoding='UTF-8'?>
<export id='19ea2e00-418f-673c-94bf-a32c2d143a87'>
  <domain>kaeru</domain>
  <title>
  </title>
  <created>1274353107</created>
  <pool></pool>
  <database>
    <name>かえる</name>
    <tags>
    </tags>
    <attribute>1</attribute>
    <notebook>
      <value>
      </value>
      <title>
      </title>
    </notebook>
    <uniq_key>f7313c64-6925-1caf-e84e-070f2b10738d</uniq_key>
    <hypervisor>2</hypervisor>
    <icon>1274172707.069426.png</icon>
  </database>
  <disks>
    <disk uuid="f7313c64-6925-1caf-e84e-070f2b10738d">
      <name>default</name>
      <path>/var/lib/libvirt/domains</path>
    </disk>
  </disks>
</export>"""

    param = ExportConfigParam()

    path = "/var/lib/libvirt/domains/8cf93333-4565-9d8e-9f19-4fbc95f9b96d/info.dat"

    # read original data file
    param.load_xml_config(path)

    # overwrite some parameters
    param.set_uuid("uuid_desu")
    param.set_domain("domain1")
    param.set_title("title1")

    # write to new file
    generator =  ExportXMLGenerator(path+".new")
    try:
        cfgxml = generator.generate(param)
    except:
        raise

    generator.writecfg(cfgxml)
