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

import sys

from os import environ as env
from mako.lookup import TemplateLookup
from securefile import SecureFile
from karesansui.lib.file.k2v import K2V
from karesansui.lib.const import LIGHTTPD_DEFAULT_PORT,\
    LIGHTTPD_DEFAULT_SSL, LIGHTTPD_DEFAULT_ACCESS

class ConfigFile(SecureFile):

    def do_read(self, conf_file):
        return conf_file.readlines()

    def do_write(self, conf_file, conf_content):
        conf_file.write(conf_content)

class LighttpdConfig(SecureFile):
    def read(self):
        try:
            from os import access, F_OK
            if access(self._path, F_OK):
                f = open(self._path, 'r')
            else:
                f = open(self._path, 'w+')

            try:
                self._SecureFile__lock_SH(f)
                try:
                    return self.do_read(f)
                finally:
                    self._SecureFile__lock_UN(f)
            finally:
                f.close()
        except Exception, e:
            print >>sys.stdout, '"%s" : Error reading config file. %s' % (self._path, e.args)
            raise

class LighttpdPortConf(LighttpdConfig):
    
    def do_read(self, f):
        port_number = LIGHTTPD_DEFAULT_PORT
        line = f.readline()
        if line:
            port_number = line.split()[2]
        return port_number

    def do_write(self, f, data):
        conf = env.get('KARESANSUI_CONF')
        _K2V = K2V(conf)
        config = _K2V.read()
 
        tmpl = TemplateLookup(directories = config['application.generate.dir'],
                                output_encoding='utf-8', input_encoding='utf-8')
        template = tmpl.get_template('/port_conf.tmpl')
        f.write(template.render(port = data.port))

class LighttpdSslConf(LighttpdConfig):

    def do_read(self, f):
        status = LIGHTTPD_DEFAULT_SSL
        lines = f.readlines()
        if lines:
            status = lines[1].split('"')[1]
        return status

    def do_write(self, f, data):
        conf = env.get('KARESANSUI_CONF')
        _K2V = K2V(conf)
        config = _K2V.read()

        tmpl = TemplateLookup(directories = config['application.generate.dir'],
                                output_encoding='utf-8', input_encoding='utf-8')
        template = tmpl.get_template('/ssl_conf.tmpl')
        f.write(template.render(ssl_status = data.ssl_status))

class LighttpdAccessConf(LighttpdConfig):
    
    def do_read(self, f):
        access_list = []
        for line in f:
            if line.find('HTTP') != -1:
                access_list.append((line.split('"')[3]))
            elif line.find('#') != -1:
                access_list.append(line.split()[1])
        if not access_list:
            access_list.append(LIGHTTPD_DEFAULT_ACCESS)

        return access_list

    def do_write(self, f, data):
        conf = env.get('KARESANSUI_CONF')
        _K2V = K2V(conf)
        config = _K2V.read()

        access_list = ''
        if data.access == 'ipaddress':
            access_list = data.ip_list
        elif data.access == 'network':
            access_list = [data.network]
        conf_value = {'access_type' : data.access, 'access_ip_list' : access_list}

        tmpl = TemplateLookup(directories = config['application.generate.dir'],
                            output_encoding='utf-8', input_encoding='utf-8')
        template = tmpl.get_template('/access_conf.tmpl')
        f.write(template.render(**conf_value))
