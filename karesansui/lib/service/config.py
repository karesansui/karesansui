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
Generate configuration file of service.xml.
</comment-en>

@file:   config.py

@author: Kei Funagayama <kei@karesansui-project.info>
"""

import os
import errno
from StringIO import StringIO
from xml.dom.minidom import DOMImplementation
implementation = DOMImplementation()

import karesansui

from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_nums_xml_xpath as XMLXpathNum, \
     get_xml_parse as XMLParse, \
     uniq_filename, r_chgrp, r_chmod

from karesansui.lib.file.configfile import ConfigFile

class KaresasnuiServiceConfigParamException(karesansui.KaresansuiLibException):
    pass

class ServiceConfigParam:

    def __init__(self, path):
        self.services = []
        self.path = path

    def findby1service(self, name):
        ret = None
        for service in self.get_services():
            if service['system_name'] == name:
                ret = service

        return ret

    def get_services(self):
        return self.services

    def set_services(self, services):
        self.services = services

    def add_service(self, system_name, system_command, system_readonly, display_name, display_description):
        self.services.append({'system_name': system_name,
                              'system_command': system_command,
                              'system_readonly':system_readonly,
                              'display_name': display_name,
                              'display_description': display_description,
                              })

    def load_xml_config(self, path=None):
        if path is not None:
            self.path = path

        if not os.path.isfile(self.path):
            raise KaresasnuiServiceConfigParamException(
                "service.xml not found. path=%s" % str(self.path))

        document = XMLParse(self.path)

        self.services = []
        service_num = XMLXpathNum(document, '/services/service')
        for n in xrange(1, service_num + 1):
            system_name = XMLXpath(document, '/services/service[%i]/system/name/text()' % n)
            system_command = XMLXpath(document, '/services/service[%i]/system/command/text()' % n)
            system_readonly = XMLXpath(document, '/services/service[%i]/system/readonly/text()' % n)
            display_name = XMLXpath(document, '/services/service[%i]/display/name/text()' % n)
            display_description = XMLXpath(document,
                                           '/services/service[%i]/display/description/text()' % n)

            self.add_service(str(system_name),
                             str(system_command),
                             str(system_readonly),
                             str(display_name),
                             str(display_description))

    def validate(self):
        pass

class ServiceXMLGenerator:

    def __init__(self, path):
        self.config_path = path

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
        out.write(tree,toxml())
        return out.getvalue()

    def writecfg(self, cfg):
        ConfigFile(self.config_path).write(cfg)
        r_chmod(self.config_path, "o-rwx")
        r_chmod(self.config_path, "g+rw")

        if os.getuid() == 0:
            r_chgrp(self.config_path, KARESANSUI_GROUP)

    def generate_xml_tree(self, config):
        config.validate()
        self.config = config
        self.begin_build()
        self.build_services()
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.services = self.document.createElement("services")
        self.document.appendChild(self.services)

    def build_services(self):
        doc = self.document

        def build_service(self, val):
            service = doc.createElement("service")
            system = doc.createElement("system")
            system.appendChild(
                self._create_text_node('name', val["system_name"]))
            system.appendChild(
                self._create_text_node('command', val["system_command"]))
            system.appendChild(
                self._create_text_node('readonly', val["system_readonly"]))

            display = doc.createElement("display")
            display.appendChild(
                self._create_text_node('name', val["display_name"]))
            display.appendChild(
                self._create_text_node('description', val["display_description"]))

            service.appendChild(system)
            service.appendChild(display)
            return service

        for service in self.config.get_services():
            self.services.appendChild(build_service(self, service))

    def end_build(self):
        pass

if __name__ == '__main__':
    orig_xml = """<?xml version='1.0' encoding='UTF-8'?>
<services>
  <service>
    <system>
      <name></name>
      <command></command>
    </system>
    <display>
      <name></name>
      <description></description>
    </display>
  </service>
</services>"""
    param = ServiceConfigParam()
    for i in xrange(10):
        param.add_service("system_name_%s" % i,
                          "system_command_%s" % i,
                          "0",
                          "display_name_%s" % i,
                          "display_description_%s" % i)

    generator =  ServiceXMLGenerator('/etc/karesansui/service.xml')
    try:
        cfgxml = generator.generate(param)
    except:
        raise

    generator.writecfg(cfgxml)
