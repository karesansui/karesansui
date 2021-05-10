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

import web
import re

import karesansui
from karesansui.lib.rest import Rest, auth
from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.rrd.rrd import RRD
from karesansui.lib.utils import is_param, is_empty, \
    str2datetime, create_epochsec, get_proc_cpuinfo, \
    get_fs_info, get_hdd_list, get_ifconfig_info, \
    get_dom_list

from karesansui.lib.const import DEFAULT_LANGS, COLLECTD_DF_RRPORT_BY_DEVICE

class HostBy1ReportBy1(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()
        self.view.host_id = host_id

        target = param[1]
        if target is None: return web.notfound()
        self.view.target = target

        group_display = False
        dev_list = []
        graph_type = []
        rrd = RRD()
        if target == "cpu":
            for dev in range(0, len(get_proc_cpuinfo())):
                if rrd.check_rrd_file_exist("cpu", dev):
                    dev_list.append(dev)
            graph_type = ['default']
        elif target == "memory":
            dev_list = ['default']
            graph_type = ['default']
        elif target == "df":
            df_list = get_fs_info()
            for fs in df_list:
                if COLLECTD_DF_RRPORT_BY_DEVICE is True:
                    dev = fs['Filesystem']
                    dev = re.sub(r'^/dev/', '', dev)
                    dev = re.sub(r'/', '_', dev)
                else:
                    dev = fs['Mounted']
                    if dev == "/":
                        dev = "root"
                    else:
                        dev = re.sub(r'^/', '', dev)
                        dev = re.sub(r'/', '_', dev)
                if rrd.check_rrd_file_exist("df", dev):
                    dev_list.append(dev)
            graph_type = ['default']

        elif target == "disk":
            group_display = True
            disk_list = get_hdd_list()
            for disk in disk_list:
                dev = disk
                dev = re.sub(r'^/dev/', '', dev)
                if rrd.check_rrd_file_exist("disk", dev):
                    dev_list.append(dev)
            graph_type = ['merged', 'octets', 'ops', 'time']

        elif target == "interface":
            group_display = True
            if_list = list(get_ifconfig_info().keys())
            for dev in if_list:
                if rrd.check_rrd_file_exist("interface", dev):
                    dev_list.append(dev)
            graph_type = ['packets', 'octets', 'errors']

        elif target == "load":
            dev_list = ['default']
            graph_type = ['default']
        elif target == "uptime":
            dev_list = ['default']
            graph_type = ['default']
        elif target == "users":
            dev_list = ['default']
            graph_type = ['default']
        elif target == "libvirt":
            virt_cpu_type = ['default']
            virt_disk_type = ['octets', 'ops']
            virt_interface_type = ['packets', 'octets', 'errors', 'dropped']
            virt_list = {}
            virt_file_exist = {}

            try:
                kvc = KaresansuiVirtConnection()

                for domname in get_dom_list():
                    virt_list[domname] = {}

                    if rrd.set_rrd_dir_host(domname) is False:
                        virt_file_exist[domname] = False
                        continue

                    try:
                        virt = kvc.search_kvg_guests(domname)[0]
                    except:
                        virt_file_exist[domname] = False
                        continue

                    virt_list[domname]['vcpu'] = {}
                    if rrd.check_rrd_file_exist("libvirt", "total", "vcpu"):
                        virt_list[domname]['vcpu']['total'] = virt_cpu_type
                    for i in range(virt.get_vcpus_info()['max_vcpus']):
                        if rrd.check_rrd_file_exist("libvirt", i, "vcpu"):
                            virt_list[domname]['vcpu'][i] = virt_cpu_type

                    virt_list[domname]['disk'] = {}
                    for disk in virt.get_disk_info():
                        if rrd.check_rrd_file_exist("libvirt", disk['target']['dev'], "disk"):
                            virt_list[domname]['disk'][disk['target']['dev']] = virt_disk_type

                    virt_list[domname]['interface'] = {}
                    for net_dev in virt.get_interface_info():
                        if rrd.check_rrd_file_exist("libvirt", net_dev['target']['dev'], "interface"):
                            virt_list[domname]['interface'][net_dev['target']['dev']] = virt_interface_type

                    if virt_list[domname]['vcpu'] == {} and \
                            virt_list[domname]['disk'] == {} and \
                            virt_list[domname]['interface'] == {}:
                        virt_list[domname] = {}
                        virt_file_exist[domname] = False
                    else:
                        virt_file_exist[domname] = True

            finally:
                kvc.close()

            self.view.virt_list = virt_list
            self.view.virt_file_exist = virt_file_exist

        self.view.group_display = group_display
        dev_list.sort()
        self.view.dev_list = dev_list
        self.view.graph_type = graph_type

        return True

urls = (
    '/host/(\d+)/report/([a-zA-Z0-9]+)/?(\.part)$', HostBy1ReportBy1,
    )

