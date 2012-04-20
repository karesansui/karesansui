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
    findby1 as w_findby1, \
    logical_delete as w_delete, \
    update as w_update

from karesansui.db.access.machine import \
    findbyhost1 as m_findbyhost1

from karesansui.lib.utils import is_param, get_karesansui_version, \
    get_proc_cpuinfo, get_proc_meminfo, get_hdd_list, \
    get_partition_info, get_ifconfig_info, get_fs_info

from karesansui.lib.conf import read_conf, write_conf

from karesansui.lib.collectd.utils import plugin_selector_to_dict, \
    create_threshold_value, threshold_value_to_dict

from karesansui.lib.collectd.config import delete_threshold, \
    set_threshold

from karesansui.lib.const import COLLECTD_PLUGIN_CPU, \
    COLLECTD_PLUGIN_DF,      COLLECTD_PLUGIN_INTERFACE, \
    COLLECTD_PLUGIN_LIBVIRT, COLLECTD_PLUGIN_MEMORY, \
    COLLECTD_PLUGIN_LOAD,    COLLECTD_LIBVIRT_TYPE, \
    COLLECTD_INTERFACE_TYPE, DEFAULT_LANGS, \
    CONTINUATION_COUNT_MIN,  CONTINUATION_COUNT_MAX, \
    PROHIBITION_PERIOD_MIN,  PROHIBITION_PERIOD_MAX, \
    FQDN_MIN_LENGTH,         FQDN_MAX_LENGTH, \
    PORT_MIN_NUMBER,         PORT_MAX_NUMBER, \
    EMAIL_MIN_LENGTH,        EMAIL_MAX_LENGTH, \
    THRESHOLD_VAL_MIN,	     WATCH_INTERVAL, \
    WATCH_PLUGINS

def validates_watch(obj):
    checker = Checker()
    check = True
    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'watch_name'):
        check = checker.check_string(_('Watch Name'),
                                     obj.input.watch_name,
                                     CHECK_EMPTY | CHECK_ONLYSPACE,
                                     None,
                                     ) and check
    else:
        check = False
        checker.add_error(_('"%s" is required.') %_('Watch Name'))

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

class HostBy1WatchBy1(Rest):
    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        watch_id = param[1]
        if watch_id is None: return web.notfound()

        watch = w_findby1(self.orm, watch_id)
        self.view.watch = watch
        self.view.plugins = WATCH_PLUGINS

        plugin_selector = plugin_selector_to_dict(watch.plugin_selector)
        self.view.plugin_selector = plugin_selector

        if watch.plugin == COLLECTD_PLUGIN_LIBVIRT:
            libvirt_type = ""
            if plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['VCPU']:
                libvirt_type = "vcpu"
            elif plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['CPU_TOTAL']:
                libvirt_type = "cpu_total"
            elif plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['DISK_OPS'] or \
                    plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['DISK_OCTETS']:
                libvirt_type = "disk"
            elif plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['IF_OCTETS'] or \
                    plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['IF_PACKETS'] or \
                    plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['IF_ERRORS'] or \
                    plugin_selector['type'] == COLLECTD_LIBVIRT_TYPE['IF_DROPPED']:
                libvirt_type = "interface"

            self.view.libvirt_type = libvirt_type

        if self.is_mode_input() is True:
            warning_value = threshold_value_to_dict(watch.warning_value)
            failure_value = threshold_value_to_dict(watch.failure_value)
            self.view.threshold_value_1 = warning_value.values()[0]
            self.view.threshold_value_2 = failure_value.values()[0]
            self.view.threshold_type = failure_value.keys()[0]
            self.view.use_percentage = watch.is_failure_percentage

            self.view.supported_langs = DEFAULT_LANGS.keys()

        self.view.memory_size = string.atol(get_proc_meminfo()["MemTotal"][0]) / 1024
        ## disk info 
        self.view.disk_size_info = {}
        for disk_data in get_fs_info():
            disk_target = re.sub(r'^/dev/', '', disk_data['Filesystem'])
            disk_target = re.sub(r'/', '_', disk_target)
            self.view.disk_size_info[disk_target] = disk_data['1048576-blocks']
        self.view.interface_type = COLLECTD_INTERFACE_TYPE
        self.view.processer_num = len(get_proc_cpuinfo().keys())
        self.view.mta = "%s:%s" % (karesansui.config['application.mail.server'],
                                   karesansui.config['application.mail.port'])
        self.view.watch_interval = WATCH_INTERVAL

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        watch_id = param[1]
        if watch_id is None: return web.notfound()

        if not validates_watch(self):
            self.logger.debug("Change watch failed. Did not validate.")
            return web.badrequest(self.view.alert)

        watch = w_findby1(self.orm, watch_id)

        ## text
        watch.name               = self.input.watch_name
        watch.continuation_count = self.input.continuation_count
        watch.prohibition_period = self.input.prohibition_period
        if is_param(self.input, 'warning_script'):
            watch.warning_script = self.input.warning_script
        else:
            watch.warning_script = ""
        if is_param(self.input, 'warning_mail_body'):
            watch.warning_mail_body = self.input.warning_mail_body
        else:
            watch.warning_mail_body = ""
        if is_param(self.input, 'failure_script'):
            watch.failure_script = self.input.failure_script
        else:
            watch.failure_script = ""
        if is_param(self.input, 'failure_mail_body'):
            watch.failure_mail_body = self.input.failure_mail_body
        else:
            watch.failure_mail_body = ""
        if is_param(self.input, 'okay_script'):
            watch.okay_script = self.input.okay_script
        else:
            watch.okay_script = ""
        if is_param(self.input, 'okay_mail_body'):
            watch.okay_mail_body = self.input.okay_mail_body
        else:
            watch.okay_mail_body = ""
        if is_param(self.input, 'notify_mail_to'):
            watch.notify_mail_to = self.input.notify_mail_to
        else:
            watch.notify_mail_to = ""
        if is_param(self.input, 'notify_mail_from'):
            watch.notify_mail_from = self.input.notify_mail_from
        else:
            watch.notify_mail_from = ""

        threshold_val1 = self.input.threshold_val1
        threshold_val2 = self.input.threshold_val2
        threshold_type = self.input.threshold_type
        if threshold_type == "max":
            warning_value = create_threshold_value(min_value=None, max_value=threshold_val1)
            failure_value = create_threshold_value(min_value=None, max_value=threshold_val2)
        elif threshold_type == "min":
            warning_value = create_threshold_value(min_value=threshold_val2, max_value=None)
            failure_value = create_threshold_value(min_value=threshold_val1, max_value=None)
        else:
            self.logger.debug("Update watch failed. Unknown threshold type.")
            return web.badrequest()

        watch.warning_value = warning_value
        watch.failure_value = failure_value

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

        watch.is_warning_percentage = bool_values.get("use_percentage")
        watch.is_warning_script     = bool_values.get("enable_warning_script")
        watch.is_warning_mail       = bool_values.get("enable_warning_mail")
        watch.is_failure_percentage = bool_values.get("use_percentage")
        watch.is_failure_script     = bool_values.get("enable_failure_script")
        watch.is_failure_mail       = bool_values.get("enable_failure_mail")
        watch.is_okay_script        = bool_values.get("enable_okay_script")
        watch.is_okay_mail          = bool_values.get("enable_okay_mail")

        w_update(self.orm, watch)

        plugin = watch.plugin
        plugin_selector = watch.plugin_selector
        modules = ["collectdplugin"]

        host = m_findbyhost1(self.orm, host_id)
        extra_args = {'include':'^threshold_'}
        #extra_args = {}
        dop = read_conf(modules, webobj=self, machine=host, extra_args=extra_args)
        if dop is False:
            self.logger.debug("Change watch failed. Failed read conf.")
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
        delete_threshold(plugin, plugin_selector, dop=dop, webobj=self, host=host)
        set_threshold(plugin,plugin_selector,params,dop=dop,webobj=self, host=host)

        extra_args = {}
        command = "/etc/init.d/collectd condrestart"
        extra_args = {"post-command": command}
        retval = write_conf(dop,  webobj=self, machine=host, extra_args=extra_args)
        if retval is False:
            self.logger.debug("Change watch failed. Failed write conf.")
            return web.internalerror('Internal Server Error. (Write Conf)')

        return web.accepted()

    @auth
    def _DELETE(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        watch_id = param[1]
        if watch_id is None: return web.notfound()

        watch = w_findby1(self.orm, watch_id)
        w_delete(self.orm, watch)

        # delete setting file
        plugin = watch.plugin
        plugin_selector = watch.plugin_selector
        modules = ["collectdplugin"]
        host_id = self.chk_hostby1(param)
        host = m_findbyhost1(self.orm, host_id)

        ## read config and delete threashold
        extra_args = {'include':'^threshold_'}
        dop = read_conf(modules, webobj=self, machine=host, extra_args=extra_args)
        if dop is False:
            self.logger.debug("Delete watch failed. Failed read conf.")
            return web.internalerror('Internal Server Error. (Read Conf)')
        delete_threshold(plugin, plugin_selector, dop=dop, webobj=self, host=host)

        ## apply setting and collectd restart
        command = "/etc/init.d/collectd condrestart"
        extra_args = {"post-command": command}
        retval = write_conf(dop, webobj=self, machine=host, extra_args=extra_args)
        if retval is False:
            self.logger.debug("Delete watch failed. Failed write conf.")
            return web.internalerror('Internal Server Error. (Write Conf)')

        return web.accepted()

urls = (
    '/host/(\d+)/watch/(\d+)/?(\.part)$', HostBy1WatchBy1,
    )
