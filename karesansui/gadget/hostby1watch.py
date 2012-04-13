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

import web
import string
import re
import karesansui

from karesansui.lib.rest import Rest, auth
from karesansui.lib.pager import Pager, validates_page
from karesansui.lib.search import validates_query

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_ONLYSPACE, \
    CHECK_LENGTH, CHECK_MIN, CHECK_MAX

from karesansui.db.access.watch import \
    findbyall as w_findbyall, findby1 as w_findby1, \
    findby1name as w_findby1name, findbyname_or_plugin as w_findbyname_or_plugin, \
    new as w_new, is_uniq_duplication as w_is_uniq_duplication, save as w_save

from karesansui.db.access.machine import \
     findby1 as m_findby1

from karesansui.lib.utils import is_param, get_karesansui_version, \
    get_proc_cpuinfo, get_proc_meminfo, get_hdd_list, \
    get_partition_info, get_ifconfig_info, get_fs_info

from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.collectd.config import set_threshold
from karesansui.db.access.machine import findbyhost1 as m_findbyhost1, \
	findbyguest1 as m_findbyguest1

from karesansui.lib.collectd.utils import  create_plugin_selector, \
     get_collectd_version, create_threshold_value

from karesansui.lib.const import WATCH_LIST_RANGE, WATCH_PLUGINS, \
    COLLECTD_PLUGIN_CPU,           COLLECTD_PLUGIN_DF, \
    COLLECTD_PLUGIN_INTERFACE,     COLLECTD_PLUGIN_LIBVIRT, \
    COLLECTD_PLUGIN_MEMORY,        COLLECTD_PLUGIN_LOAD, \
    COLLECTD_CPU_TYPE,             COLLECTD_CPU_TYPE_INSTANCE, \
    COLLECTD_CPU_DS,               COLLECTD_MEMORY_TYPE, \
    COLLECTD_MEMORY_TYPE_INSTANCE, COLLECTD_MEMORY_DS,\
    COLLECTD_DF_TYPE,              COLLECTD_DF_DS, \
    COLLECTD_INTERFACE_TYPE,       COLLECTD_INTERFACE_DS, \
    COLLECTD_LIBVIRT_TYPE,         COLLECTD_LOAD_TYPE, \
    COLLECTD_LOAD_DS,              DEFAULT_LANGS, \
    CONTINUATION_COUNT_MIN,        CONTINUATION_COUNT_MAX, \
    PROHIBITION_PERIOD_MIN,        PROHIBITION_PERIOD_MAX, \
    FQDN_MIN_LENGTH,               FQDN_MAX_LENGTH, \
    PORT_MIN_NUMBER,               PORT_MAX_NUMBER, \
    EMAIL_MIN_LENGTH,              EMAIL_MAX_LENGTH, \
    THRESHOLD_VAL_MIN, \
    DEFAULT_ALERT_TRIGGER_COUNT, DEFAULT_SLIENT_PERIOD

def validates_watch(obj):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'watch_name'):
        check = checker.check_string(_('Name'),
                                     obj.input.watch_name,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Name'))

    if is_param(obj.input, 'watch_target'):
        check = checker.check_string(_('Watch Target'),
                                     obj.input.watch_target,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     ) and check
        if obj.input.watch_target not in WATCH_PLUGINS.values():
            check = False
            # TRANSLATORS:
            #  %sは監視対象ではありません。
            checker.add_error(_('"%s" is not watch target.') %_(obj.input.watch_target))
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Watch Target'))

    if is_param(obj.input, 'continuation_count'):
        check = checker.check_number(_('Alert Trigger Count'),
                                     obj.input.continuation_count,
                                     CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     CONTINUATION_COUNT_MIN,
                                     CONTINUATION_COUNT_MAX,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Alert Trigger Count'))

    if is_param(obj.input, 'prohibition_period'):
        check = checker.check_number(_('Silent Period'),
                                     obj.input.prohibition_period,
                                     CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                                     PROHIBITION_PERIOD_MIN,
                                     PROHIBITION_PERIOD_MAX,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Silent Period'))

    if is_param(obj.input, 'threshold_fraction'):
        fraction = int(obj.input.threshold_fraction)
    else:
        fraction = 0

    if is_param(obj.input, 'threshold_val1'):
        if fraction == 0:
            check = checker.check_number(_('Threshold Value'),
                                         obj.input.threshold_val1,
                                         CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                                         THRESHOLD_VAL_MIN,
                                         None,
                                         ) and check
        else:
            check = checker.check_fraction(_('Threshold Value'),
                                           obj.input.threshold_val1,
                                           CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                                           THRESHOLD_VAL_MIN,
                                           None,
                                           fraction,
                                           ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Threshold Value'))

    if is_param(obj.input, 'threshold_val2'):
        if fraction == 0:
            check = checker.check_number(_('Threshold Value'),
                                         obj.input.threshold_val2,
                                         CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                                         THRESHOLD_VAL_MIN,
                                         None,
                                         ) and check
        else:
            check = checker.check_fraction(_('Threshold Value'),
                                           obj.input.threshold_val2,
                                           CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                                           THRESHOLD_VAL_MIN,
                                           None,
                                           fraction,
                                           ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Threshold Value'))

    if not is_param(obj.input, 'threshold_type'):
        check = False
        checker.add_error(_('"%s" is required.') %_('Threshold Type'))

    if is_param(obj.input, 'notify_mail_to'):
        if obj.input.notify_mail_to != "":
            check = checker.check_mailaddress(_('Mail To'),
                                              obj.input.notify_mail_to,
                                              CHECK_LENGTH | CHECK_VALID,
                                              EMAIL_MIN_LENGTH,
                                              EMAIL_MAX_LENGTH,
                                              ) and check

    if is_param(obj.input, 'notify_mail_from'):
        if obj.input.notify_mail_from != "":
            check = checker.check_mailaddress(_('Mail From'),
                                              obj.input.notify_mail_from,
                                              CHECK_LENGTH | CHECK_VALID,
                                              EMAIL_MIN_LENGTH,
                                              EMAIL_MAX_LENGTH,
                                              ) and check

    obj.view.alert = checker.errors
    return check

class HostBy1Watch(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if self.is_mode_input() is True:
            self.view.plugins = WATCH_PLUGINS
            self.view.cpu_type_instance = COLLECTD_CPU_TYPE_INSTANCE
            self.view.memory_type_instance = COLLECTD_MEMORY_TYPE_INSTANCE
            self.view.df_ds = COLLECTD_DF_DS
            self.view.interface_type = COLLECTD_INTERFACE_TYPE
            self.view.interface_ds = COLLECTD_INTERFACE_DS
            self.view.load_ds = COLLECTD_LOAD_DS

            cpu_logical_number = len(get_proc_cpuinfo())
            self.view.cpu_logical_number = range(1, cpu_logical_number+1)
            self.view.memory_size = string.atol(get_proc_meminfo()["MemTotal"][0]) / 1024
            self.view.df_list = get_fs_info()
            self.view.interface_list = get_ifconfig_info().keys()

            ## guest os list
            from karesansui.lib.utils import get_dom_list
            from karesansui.lib.virt.virt import KaresansuiVirtConnection
            from karesansui.lib.merge import MergeGuest
            self.view.dom_list = get_dom_list()

            dom_info = {}
            for domname in get_dom_list():
                kvc = KaresansuiVirtConnection()
                virt = kvc.search_kvg_guests(domname)[0]
                dom_info[domname] = {}
                dom_info[domname]['network'] = []
                dom_info[domname]['disk'] = []
                dom_info[domname]['disk_size'] = {}
                for net_dev in virt.get_interface_info():
                    dom_info[domname]['network'].append(net_dev['target']['dev'])
                for disk in virt.get_disk_info():
                    dom_info[domname]['disk'].append(disk['target']['dev'])
                    dom_info[domname]['disk_size'][disk['target']['dev']] = disk['source']['size']

                dom_info[domname]['vcpu'] = virt.get_vcpus_info()['max_vcpus']
                kvc.close()
            self.view.dom_info = dom_info

            ## disk info 
            self.view.disk_size_info = {}
            for disk_data in get_fs_info():
                self.view.disk_size_info[disk_data['Filesystem']] = disk_data['1048576-blocks']

            self.view.processer_num = len(get_proc_cpuinfo().keys())
            self.view.supported_langs = DEFAULT_LANGS.keys()
            self.view.myaddress = self.me.email
            self.view.mta = "%s:%s" % (karesansui.config['application.mail.server'],
                                       karesansui.config['application.mail.port'])
            self.view.alert_trigger_count = DEFAULT_ALERT_TRIGGER_COUNT;
            self.view.slient_period = DEFAULT_SLIENT_PERIOD;
            return True

        if not validates_query(self):
            self.logger.debug("Show watch is failed, "
                              "Invalid query value "
                              "- query=%s" % self.input.q)
            return web.badrequest(self.view.alert)

        if not validates_page(self):
            self.logger.debug("Show watch is failed, "
                              "Invalid page value - page=%s" % self.input.p)
            return web.badrequest(self.view.alert)

        if is_param(self.input, 'q') is True:
            watchs = w_findbyname_or_plugin(self.orm, self.input.q)
            if not watchs:
                self.logger.debug("Show watch is failed, "
                                  "Could not find watch "
                                  "- query=%s" % self.input.q)
                return web.nocontent()
            self.view.search_value = self.input.q
        else:
            watchs = w_findbyall(self.orm)
            self.view.search_value = ""

        if is_param(self.input, 'p') is True:
            start = int(self.input.p)
        else:
            start = 0

        pager = Pager(watchs, start, WATCH_LIST_RANGE)
        if not pager.exist_now_page() and is_param(self.input, 'p') is True:
            self.logger.debug("Show watch is failed, "
                              "Could not find page - page=%s" % self.input.p)
            return web.nocontent()

        self.view.pager = pager
        self.view.input = self.input

        return True

    @auth
    def _POST(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        if not validates_watch(self):
            self.logger.debug("Set watch failed. Did not validate.")
            return web.badrequest(self.view.alert)

        plugin = self.input.watch_target
        plugin_instance = None
        type = None
        type_instance = None
        plugin_ds = None
        libvirt_host = None

        if plugin == COLLECTD_PLUGIN_CPU:
            #cpu method
            plugin_instance = string.atoi(self.input.logical_cpu_number) - 1
            type_instance = self.input.cpu_status
            type = COLLECTD_CPU_TYPE
            plugin_ds = COLLECTD_CPU_DS

        elif plugin == COLLECTD_PLUGIN_MEMORY:
            #memory method
            type_instance = self.input.memory_status
            type = COLLECTD_MEMORY_TYPE
            plugin_ds = COLLECTD_MEMORY_DS

        elif plugin == COLLECTD_PLUGIN_DF:
            #df method
            type = COLLECTD_DF_TYPE
            type_instance = self.input.df_target_fs
            type_instance = re.sub(r'^/dev/', '', type_instance)
            type_instance = re.sub(r'/', '_', type_instance)
            plugin_ds = self.input.df_disk_status

        elif plugin == COLLECTD_PLUGIN_INTERFACE:
            #interface method
            type = self.input.network_status
            type_instance = self.input.network_target_interface
            plugin_ds = self.input.network_direction

        elif plugin == COLLECTD_PLUGIN_LIBVIRT:
            #libvirt method
            libvirt_host = self.input.libvirt_target_machine
            if self.input.libvirt_target == "cpu":
                if self.input.libvirt_vcpu_target == "total":
                    type = COLLECTD_LIBVIRT_TYPE['CPU_TOTAL']
                else:
                    type = COLLECTD_LIBVIRT_TYPE['VCPU']
                    type_instance = self.input.libvirt_vcpu_target

                plugin_ds = COLLECTD_CPU_DS

            elif self.input.libvirt_target == "disk":
                type = COLLECTD_LIBVIRT_TYPE['DISK_OCTETS']
                type_instance = self.input.libvirt_disk_target
                plugin_ds = self.input.libvirt_disk_value_type

            elif self.input.libvirt_target == "network":
                type = "if_" + self.input.libvirt_network_status
                type_instance = self.input.libvirt_target_interface
                plugin_ds = self.input.libvirt_network_direction

        elif plugin == COLLECTD_PLUGIN_LOAD:
            #load method
            type = COLLECTD_LOAD_TYPE
            plugin_ds = self.input.load_term

        else:
            self.logger.debug("Set watch failed. Unknown plugin type.")
            return web.badrequest()

        plugin_selector = create_plugin_selector(plugin_instance, type, type_instance, plugin_ds, libvirt_host)

        ## text
        continuation_count = self.input.continuation_count
        prohibition_period = self.input.prohibition_period
        threshold_val1     = self.input.threshold_val1
        threshold_val2     = self.input.threshold_val2
        threshold_type     = self.input.threshold_type
        if is_param(self.input, 'warning_script'):
            warning_script = self.input.warning_script
        else:
            warning_script = ""
        if is_param(self.input, 'warning_mail_body'):
            warning_mail_body = self.input.warning_mail_body
        else:
            warning_mail_body = ""
        if is_param(self.input, 'failure_script'):
            failure_script = self.input.failure_script
        else:
            failure_script = ""
        if is_param(self.input, 'failure_mail_body'):
            failure_mail_body = self.input.failure_mail_body
        else:
            failure_mail_body = ""
        if is_param(self.input, 'okay_script'):
            okay_script = self.input.okay_script
        else:
            okay_script = ""
        if is_param(self.input, 'okay_mail_body'):
            okay_mail_body = self.input.okay_mail_body
        else:
            okay_mail_body = ""
        if is_param(self.input, 'notify_mail_to'):
            notify_mail_to = self.input.notify_mail_to
        else:
            notify_mail_to = ""
        if is_param(self.input, 'notify_mail_from'):
            notify_mail_from = self.input.notify_mail_from
        else:
            notify_mail_from = ""

        ## bool
        bool_input_key = ["use_percentage", "enable_warning_mail",
                          "enable_failure_mail", "enable_okay_mail",
                          "enable_warning_script", "enable_failure_script",
                          "enable_okay_script"]
        bool_values = {}
        for key in bool_input_key:
            if self.input.has_key(key):
                bool_values.update({key:True})
            else:
                bool_values.update({key:False})

        if threshold_type == "max":
            warning_value = create_threshold_value(min_value=None, max_value=threshold_val1)
            failure_value = create_threshold_value(min_value=None, max_value=threshold_val2)
        elif threshold_type == "min":
            warning_value = create_threshold_value(min_value=threshold_val2, max_value=None)
            failure_value = create_threshold_value(min_value=threshold_val1, max_value=None)
        else:
            self.logger.debug("Set watch failed. Unknown threshold type.")
            return web.badrequest()

        machine = m_findby1(self.orm, host_id)

        if w_is_uniq_duplication(self.orm, machine, plugin, plugin_selector) is True:
            self.logger.debug("Set watch failed. Duplicate watch DB.")
            return web.badrequest("Set watch failed. Duplication watch")

        _watch = w_new(created_user          = self.me,
                       modified_user         = self.me,
                       name                  = self.input.watch_name,
                       plugin                = plugin,
                       plugin_selector       = plugin_selector,
                       karesansui_version    = get_karesansui_version(),
                       collectd_version      = get_collectd_version(),
                       machine               = machine,
                       continuation_count    = continuation_count,
                       prohibition_period    = prohibition_period,
                       warning_value         = warning_value,
                       is_warning_percentage = bool_values.get("use_percentage"),
                       is_warning_script     = bool_values.get("enable_warning_script"),
                       warning_script        = warning_script,
                       is_warning_mail       = bool_values.get("enable_warning_mail"),
                       warning_mail_body     = warning_mail_body,
                       failure_value         = failure_value,
                       is_failure_percentage = bool_values.get("use_percentage"),
                       is_failure_script     = bool_values.get("enable_failure_script"),
                       failure_script        = failure_script,
                       is_failure_mail       = bool_values.get("enable_failure_mail"),
                       failure_mail_body     = failure_mail_body,
                       is_okay_script        = bool_values.get("enable_okay_script"),
                       okay_script           = okay_script,
                       is_okay_mail          = bool_values.get("enable_okay_mail"),
                       okay_mail_body        = okay_mail_body,
                       notify_mail_to        = notify_mail_to,
                       notify_mail_from      = notify_mail_from,
                       is_deleted            = False,
                       )
        w_save(self.orm, _watch)

        modules = ["collectdplugin"]

        host = m_findbyhost1(self.orm, host_id)
        extra_args = {'include':'^threshold_'}
        #extra_args = {}
        dop = read_conf(modules, webobj=self, machine=host, extra_args=extra_args)
        if dop is False:
            self.logger.debug("Set watch failed. Failed read conf.")
            return web.internalerror('Internal Server Error. (Read Conf)')

        params = {}
        if threshold_type == "max":
            params['WarningMax'] = str(threshold_val1)
            params['FailureMax'] = str(threshold_val2)
        elif threshold_type == "min":
            params['WarningMin'] = str(threshold_val2)
            params['FailureMin'] = str(threshold_val1)

        params['Percentage'] = str(bool_values.get("use_percentage")).lower()
        params['Persist']    = "true"
        set_threshold(plugin,plugin_selector,params,dop=dop,webobj=self, host=host)

        extra_args = {}
        command = "/etc/init.d/collectd condrestart"
        extra_args = {"post-command": command}
        retval = write_conf(dop,  webobj=self, machine=host, extra_args=extra_args)
        if retval is False:
            self.logger.debug("Set watch failed. Failed write conf.")
            return web.internalerror('Internal Server Error. (Write Conf)')

        return web.created(None)

urls = (
    '/host/(\d+)/watch/?(\.part)$', HostBy1Watch,
    )
