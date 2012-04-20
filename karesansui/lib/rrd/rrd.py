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

import re
import os

import karesansui
from karesansui.lib.rrd.cpu       import create_cpu_graph, is_cpu_file_exist
from karesansui.lib.rrd.memory    import create_memory_graph
from karesansui.lib.rrd.df        import create_df_graph, is_df_file_exist
from karesansui.lib.rrd.disk      import create_disk_graph, is_disk_file_exist
from karesansui.lib.rrd.interface import create_interface_graph, is_interface_file_exist
from karesansui.lib.rrd.load      import create_load_graph
from karesansui.lib.rrd.uptime    import create_uptime_graph
from karesansui.lib.rrd.users     import create_users_graph
from karesansui.lib.rrd.libvirt   import create_libvirt_cpu_graph, \
                                         create_libvirt_disk_graph, \
                                         create_libvirt_interface_graph, \
                                         is_libvirt_cpu_file_exist, \
                                         is_libvirt_disk_file_exist, \
                                         is_libvirt_interface_file_exist

from karesansui.lib.const import COLLECTD_DATA_DIR, KARESANSUI_TMP_DIR
from karesansui.lib.utils import get_hostname, locale_dummy

class RRD:
    _graph_dir = KARESANSUI_TMP_DIR
    _rrd_dir = "%s/%s" % (COLLECTD_DATA_DIR, get_hostname())
    _lang = "en_US"
    _ = None

    def __init__(self, locale=None, lang=None, graph_dir=None, rrd_dir=None):
        if locale is not None:
            self.set_locale(locale)
        else:
            self._ = locale_dummy

        if lang is not None:
            self.set_lang(lang)

        if graph_dir is not None:
            self.set_graph_dir(graph_dir)

        if rrd_dir is not None:
            self.set_rrd_dir(rrd_dir)

    def get_graph_dir(self):
        return self._graph_dir

    def get_rrd_dir(self):
        return self._rrd_dir

    def get_locale(self):
        return self._

    def get_lang(self):
        return self._lang

    def set_graph_dir(self, path):
        ret = False
        if os.path.isdir(path) is True:
            self._graph_dir = path
            ret = True
        return ret

    def set_rrd_dir(self, path):
        ret = False
        if os.path.isdir(path) is True:
            self._rrd_dir = path
            ret = True
        return ret

    def set_rrd_dir_host(self, host):
        ret = False
        rrd_dir = "%s/%s" % (COLLECTD_DATA_DIR, str(host))
        if os.path.isdir(rrd_dir) is True:
            self._rrd_dir = rrd_dir
            ret = True
        return ret

    def set_locale(self, locale):
        ret = False
        if locale is not None:
            self._ = locale
            ret = True
        return ret

    def set_lang(self, lang):
        ret = False
        if lang is not None:
            self._lang = lang
            ret = True
        return ret

    def check_rrd_file_exist(self, target, dev, libvirt_target=None):
        ret = False

        if target == "cpu":
            ret = is_cpu_file_exist(self._rrd_dir, dev)
        elif target == "df":
            ret = is_df_file_exist(self._rrd_dir, dev)
        elif target == "disk":
            ret = is_disk_file_exist(self._rrd_dir, dev)
        elif target == "interface":
            ret = is_interface_file_exist(self._rrd_dir, dev)
        elif target == "libvirt":
            if libvirt_target == "vcpu":
                ret = is_libvirt_cpu_file_exist(self._rrd_dir, dev)
            elif libvirt_target == "disk":
                ret = is_libvirt_disk_file_exist(self._rrd_dir, dev)
            elif libvirt_target == "interface":
                ret = is_libvirt_interface_file_exist(self._rrd_dir, dev)

        return ret

    def create_graph(self, target, dev, type, start, end, libvirt_target=None):
        target = str(target)
        dev    = str(dev)
        type   = str(type)
        start  = str(start)
        end    = str(end)

        filepath = ""
        if target == "cpu":
            filepath = create_cpu_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "memory":
            filepath = create_memory_graph(self._, self._lang,  self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "df":
            filepath = create_df_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "disk":
            filepath = create_disk_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "interface":
            filepath = create_interface_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "load":
            filepath = create_load_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "uptime":
            filepath = create_uptime_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "users":
            filepath = create_users_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
        elif target == "libvirt":
            if libvirt_target == "vcpu":
                filepath = create_libvirt_cpu_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
            elif libvirt_target == "disk":
                filepath = create_libvirt_disk_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)
            elif libvirt_target == "interface":
                filepath = create_libvirt_interface_graph(self._, self._lang, self._graph_dir, self._rrd_dir, start, end, dev, type)

        return filepath
