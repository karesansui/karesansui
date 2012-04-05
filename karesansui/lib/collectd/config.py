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

import os
import re
import sys
import types

from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.utils import uniq_sort
from karesansui.lib.utils import preprint_r
from karesansui.lib.collectd.utils import create_plugin_selector, plugin_selector_to_dict
from karesansui.lib.const import VENDOR_PREFIX, KARESANSUI_PREFIX, \
                                 VENDOR_DATA_DIR, \
                                 COUNTUP_DATABASE_PATH, COLLECTD_LOG_DIR, \
                                 COLLECTD_DF_RRPORT_BY_DEVICE

from karesansui.lib.parser.collectdplugin import PARSER_COLLECTD_PLUGIN_DIR

MODULE = "collectd"

DictOp = None

DEFAULT_KARESANSUI_CONF = "/etc/karesansui/application.conf"

COLLECTD_PLUGIN_DIR = "%s/lib64/collectd" % VENDOR_PREFIX
if os.path.exists(COLLECTD_PLUGIN_DIR):
    COLLECTD_PLUGIN_DIR = "%s/lib/collectd" % VENDOR_PREFIX

COLLECTD_SHARE_DIR         = "%s/share/collectd" % VENDOR_PREFIX
KARESANSUI_PYTHON_PATH     = "%s/lib/python" % KARESANSUI_PREFIX
COLLECTD_PYTHON_MODULE_DIR = "%s/karesansui/lib/collectd" % KARESANSUI_PYTHON_PATH

COLLECTD_DATA_DIR          = "%s/collectd" % VENDOR_DATA_DIR
COLLECTD_PID_FILE          = "/var/run/collectd.pid"

#COLLECTD_PLUGINS = ["cpu", "df", "disk", "exec", "interface", "iptables", "libvirt", "load", "logfile", "memory", "network", "python", "rrdcached", "rrdtool", "sensors", "snmp", "syslog", "tail", "uptime", "users"]
#COLLECTD_PLUGINS = ["cpu", "df", "disk", "interface", "libvirt", "load", "logfile", "memory", "python", "rrdcached", "rrdtool", "sensors", "syslog"]
COLLECTD_PLUGINS = ["cpu", "df", "disk", "interface", "libvirt", "load", "logfile", "memory", "python", "rrdtool"]

def _get_collectd_config(webobj=None, host=None):
    modules = ["collectd","collectdplugin"]

    dop = read_conf(modules, webobj, host)
    if dop is False:
        return False

    return dop

DictOp = _get_collectd_config()

def get_collectd_param(param=None, section=None, dop=None, webobj=None, host=None):
    global DictOp
    retval = None

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    if section is None:
        if dop.cdp_isset("collectd",[param]) is True:
            return dop.cdp_get("collectd",[param])
    else:
        if not "collectdplugin" in dop.ModuleNames:
            dop.addconf("collectdplugin",{})

        from karesansui.lib.parser.collectdplugin import collectdpluginParser
        if dop.cdp_isset("collectdplugin",[section,"Plugin",section],multiple_file=True) is False:
            extra_args = {"include":"^(%s)$" % section}
            new_conf_arr =  collectdpluginParser().read_conf(extra_args)

            for _k,_v in new_conf_arr.iteritems():
                if _k[0:1] != "@":
                    dop.set("collectdplugin",[_k],_v['value'])

        if dop.cdp_isset("collectdplugin",[section,"Plugin",section,param],multiple_file=True) is True:
            return dop.cdp_get("collectdplugin",[section,"Plugin",section,param],multiple_file=True)

def plugin_list(webobj=None, host=None, dop=None):
    global DictOp
    retval = []

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    try:
        load_plugins = dop.query("collectd",["LoadPlugin"])
        if load_plugins is False:
            load_plugins = []
    except:
        load_plugins = []

    try:
        plugins = dop.getconf("collectdplugin")
        for _k,_v in plugins.iteritems():
            _load_plugins = dop.query("collectdplugin",[_k,"LoadPlugin"])
            if type(_load_plugins) is list or (_load_plugins is not False and len(_load_plugins) > 0):
                load_plugins = load_plugins + _load_plugins
        del plugins
    except:
        pass

    retval = uniq_sort(load_plugins)
    return retval

def active_plugin_list(webobj=None, host=None, dop=None):
    global DictOp
    retval = []

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    list = plugin_list(dop, webobj, host)
    #preprint_r(list)
    for plugin_name in list:
        iscomment = True
        if dop.isset("collectd",["LoadPlugin",plugin_name]) is True:
            iscomment = dop.iscomment("collectd",["LoadPlugin",plugin_name])

        if iscomment is True:
            plugins = dop.getconf("collectdplugin")
            for _k,_v in plugins.iteritems():
                if dop.isset("collectdplugin",[_k,"LoadPlugin",plugin_name]) is True:
                    iscomment = dop.iscomment("collectdplugin",[_k,"LoadPlugin",plugin_name])
                    break
            del plugins
        if iscomment is False:
            retval.append(plugin_name)

    return retval

def inactive_plugin_list(dop=None, webobj=None, host=None):
    global DictOp
    retval = []

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    list = plugin_list(dop, webobj, host)
    active = active_plugin_list(dop, webobj, host)
    for plugin_name in list:
        if not plugin_name in active:
            retval.append(plugin_name)

    return retval

def is_enabled_plugin(plugin_name, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    active = active_plugin_list(dop, webobj, host)
    if plugin_name in active:
        retval = True

    return retval

def enabled_plugin(plugin_name, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    active = active_plugin_list(dop, webobj, host)
    if not plugin_name in active:
        if dop.cdp_isset("collectd",["LoadPlugin",plugin_name]) is True:
            retval = dop.cdp_uncomment("collectd",["LoadPlugin",plugin_name])
        else:
            plugins = dop.getconf("collectdplugin")
            for _k,_v in plugins.iteritems():
                if dop.cdp_isset("collectdplugin",[_k,"LoadPlugin",plugin_name],multiple_file=True) is True:
                    retval = dop.cdp_uncomment("collectdplugin",[_k,"LoadPlugin",plugin_name],multiple_file=True)
                    break
            del plugins

    return retval

def disabled_plugin(plugin_name, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    active = active_plugin_list(dop, webobj, host)
    if plugin_name in active:
        if dop.cdp_isset("collectd",["LoadPlugin",plugin_name]) is True:
            retval = dop.cdp_comment("collectd",["LoadPlugin",plugin_name])
        else:
            plugins = dop.getconf("collectdplugin")
            for _k,_v in plugins.iteritems():
                if dop.cdp_isset("collectdplugin",[_k,"LoadPlugin",plugin_name],multiple_file=True) is True:
                    retval = dop.cdp_comment("collectdplugin",[_k,"LoadPlugin",plugin_name],multiple_file=True)
                    break
            del plugins

    return retval


def get_global_parameter(name, dop=None, webobj=None, host=None):
    global DictOp

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    retval = dop.cdp_get("collectd",[name])

    if retval is False:
        retval = dop.get("collectd",[name])

    return retval

def set_global_parameter(name, value, dop=None, webobj=None, host=None, is_cdp=True):
    global DictOp

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    if is_cdp is True:
        return dop.cdp_set("collectd",[name],value)
    else:
        return dop.set("collectd",[name],value)

def where_is_plugin(plugin_name, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    keyword = "LoadPlugin"
    keyword = "Plugin"

    if dop.cdp_isset("collectd",[keyword,plugin_name]) is True:
        retval = "@global"

    plugins = dop.getconf("collectdplugin")
    for _k,_v in plugins.iteritems():
        if dop.cdp_isset("collectdplugin",[_k,keyword,plugin_name]) is True:
            retval = _k
            break
    del plugins

    return retval

def switch_python_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "python"

    # まだ読み込まれていなければ読み込む
    from karesansui.lib.parser.collectdplugin import collectdpluginParser
    if dop.isset("collectdplugin",[configName]) is False:
        extra_args = {"include":"^(%s)$" % configName}
        new_conf_arr =  collectdpluginParser().read_conf(extra_args)
        for _k,_v in new_conf_arr.iteritems():
            if _k[0:1] != "@":
                dop.set("collectdplugin",[_k],_v['value'])

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","python","Globals"],"true",multiple_file=True)

    _keys = [configName,"Plugin","python"]

    keys = _keys + ["ModulePath"]
    value = "\"%s\"" % COLLECTD_PYTHON_MODULE_DIR
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Encoding"]
    value = "utf-8"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["LogTraces"]
    value = "true"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Interactive"]
    value = "false"
    dop.cdp_comment("collectdplugin",keys,multiple_file=True)
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Import"]
    value = "\"notification\""
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Module","notification","CountupDBPath"]
    value = "\"%s\"" % COUNTUP_DATABASE_PATH
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Module","notification","LogFile"]
    value = "\"%s/notification.log\"" % COLLECTD_LOG_DIR
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Module","notification","LogLevel"]
    value = "7"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Module","notification","Environ"]
    envs = []
    try:
        envs.append("LANG=%s" % os.environ["LANG"])
    except:
        pass
    try:
        envs.append("KARESANSUI_CONF=%s" % os.environ["KARESANSUI_CONF"])
    except:
        envs.append("KARESANSUI_CONF=%s" % DEFAULT_KARESANSUI_CONF)
        pass
    value = "\"" + "\" \"".join(envs) + "\""
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","python"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","python"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_python_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_python_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_python_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_python_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_syslog_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "syslog"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","syslog"],"syslog",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","syslog"]

    keys = _keys + ["LogLevel"]
    value = "\"info\""   # debug|info|notice|warning|err
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","syslog"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","syslog"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_syslog_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_syslog_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_syslog_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_syslog_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_logfile_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "logfile"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","logfile"],"logfile",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","logfile"]

    keys = _keys + ["LogLevel"]
    value = "\"debug\""   # debug|info|notice|warning|err
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Timestamp"]
    value = "true"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["File"]
    value = "\"%s/collectd.log\"" % COLLECTD_LOG_DIR
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["PrintSeverity"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","logfile"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","logfile"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_logfile_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_logfile_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_logfile_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_logfile_plugin(flag=False, dop=dop, webobj=webobj, host=host)



def switch_rrdtool_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "rrdtool"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","rrdtool"],"rrdtool",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","rrdtool"]

    keys = _keys + ["DataDir"]
    value = "\"%s\"" % COLLECTD_DATA_DIR
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["CacheTimeout"]
    value = "120"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["CacheFlush"]
    value = "900"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["RandomTimeout"]
    #value = "60"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["StepSize"]
    #value = "30"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["HeartBeat"]
    #value = "120"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["WritesPerSecond"]
    #value = "500"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["RRARows"]
    #value = "2400"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["RRATimespan"]
    #value = "144000"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    #keys = _keys + ["XFF"]
    #value = "0.1"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","rrdtool"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","rrdtool"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_rrdtool_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_rrdtool_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_rrdtool_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_rrdtool_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_rrdcached_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "rrdcached"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","rrdcached"],"rrdcached",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","rrdcached"]

    keys = _keys + ["DataDir"]
    value = "\"%s\"" % COLLECTD_DATA_DIR
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["DaemonAddress"]
    value = "\"unix:/var/run/rrdcached/rrdcached.sock\""
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["CreateFiles"]
    value = "true"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["CollectStatistics"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","rrdcached"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","rrdcached"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_rrdcached_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_rrdcached_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_rrdcached_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_rrdcached_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_memory_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "memory"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","memory"],"memory",multiple_file=True,is_opt_multi=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","memory"],recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","memory"],recursive=True,multiple_file=True)

def enable_memory_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_memory_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_memory_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_memory_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_cpu_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "cpu"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","cpu"],"cpu",multiple_file=True,is_opt_multi=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","cpu"],recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","cpu"],recursive=True,multiple_file=True)

def enable_cpu_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_cpu_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_cpu_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_cpu_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_disk_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "disk"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","disk"],"disk",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","disk"]

    keys = _keys + ["Disk"]
    value = "\"/^(([hs]|xv)d[a-f][0-9]?|([a-z]+\/)?c[0-9]d[0-9](p[0-9])?)$/\""
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["IgnoreSelected"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","disk"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","disk"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_disk_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_disk_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_disk_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_disk_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_df_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "df"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","df"],"df",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","df"]

    keys = _keys + ["ReportReserved"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["ReportInodes"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["ReportByDevice"]
    value = "%s" % str(COLLECTD_DF_RRPORT_BY_DEVICE).lower()
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["MountPoint"]
    #value = "\"/^\/(home|var|boot|usr)?/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全て対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    keys = _keys + ["Device"]
    #value = "192.168.0.2:/mnt/nfs"
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全て対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    keys = _keys + ["FSType"]
    #value = "\"/^(ext[234]|reiserfs|xfs|jfs)$/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全て対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    # 上記３つ(MountPoint,Device,FSType)で指定されたものを対象外にする場合はtrue
    keys = _keys + ["IgnoreSelected"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","df"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","df"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_df_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_df_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_df_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_df_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_interface_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "interface"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","interface"],"interface",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","interface"]

    keys = _keys + ["Interface"]
    #value = "\"/(eth[0-9]|lo|vif|virbr|xenbr)/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全て対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    # 上記Interfaceで指定されたものを対象外にする場合はtrue
    keys = _keys + ["IgnoreSelected"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","interface"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","interface"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_interface_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_interface_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_interface_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_interface_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_libvirt_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "libvirt"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","libvirt"],"libvirt",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","libvirt"]

    keys = _keys + ["HostnameFormat"]
    value = "name" # hostname|name|uuid
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    from karesansui.lib.utils import available_virt_mechs, available_virt_uris
    keys = _keys + ["Connection"]
    mech = available_virt_mechs()[0]
    value = "\"%s\"" % available_virt_uris()[mech]
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["Domain"]
    # 正規表現指定が可能
    #value = "\"/[^ ]+/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全てのドメインが対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    # 対象インターフェース指定(ドメイン名:デバイス名)
    keys = _keys + ["InterfaceDevice"]
    # 正規表現指定が可能
    #value = "\"/:eth[0-9\:]+/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全てのインターフェースが対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    # 対象ブロックデバイス指定(ドメイン名:デバイス名)
    keys = _keys + ["BlockDevice"]
    # 正規表現指定が可能
    #value = "\"/:(([hs]|xv)d[a-f][0-9]?|([a-z]+\/)?c[0-9]d[0-9](p[0-9])?)/\""
    #dop.cdp_set("collectdplugin",keys,value,multiple_file=True)
    # 指定しないときは、全てのインターフェースが対象になる
    dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    # 上記２つの対象デバイス指定で指定されたデバイスを対象外にする場合はtrue
    keys = _keys + ["IgnoreSelected"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    keys = _keys + ["RefreshInterval"]
    value = "60"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","libvirt"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","libvirt"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_libvirt_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_libvirt_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_libvirt_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_libvirt_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_sensors_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "sensors"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","sensors"],"sensors",multiple_file=True,is_opt_multi=True)

    _keys = [configName,"Plugin","sensors"]


    # 既存の設定を削除
    keys = _keys + ["Sensor"]
    if dop.cdp_isset("collectdplugin",keys,multiple_file=True) is True:
        for _k in dop.cdp_get("collectdplugin",keys,multiple_file=True).keys():
            keys = _keys + ["Sensor",_k]
            dop.cdp_delete("collectdplugin",keys,multiple_file=True)

    orders_key = _keys + ["Sensor","@ORDERS"]
    dop.cdp_unset("collectplugin",orders_key,multiple_file=True)
    orders = []

    #from karesansui.lib.utils import get_sensor_chip_name
    #chip_name = get_sensor_chip_name()
    chip_name = "it8712-isa-0290"

    # temperature
    for _temp in ["temp","temp1","temp2","temp3","temp4","temp5","temp6","temp7"]:
        sensor_id = "%s/temperature-%s" % (chip_name,_temp)
        value = "\"%s\"" % sensor_id
        keys = _keys + ["Sensor",value]
        dop.cdp_set("collectdplugin",keys,value,multiple_file=True,is_opt_multi=True)
        orders.append([value])

    # fanspeed
    for _fan in ["fan1","fan2","fan3","fan4","fan5","fan6","fan7"]:
        sensor_id = "%s/fanspeed-%s" % (chip_name,_fan)
        value = "\"%s\"" % sensor_id
        keys = _keys + ["Sensor",value]
        dop.cdp_set("collectdplugin",keys,value,multiple_file=True,is_opt_multi=True)
        orders.append([value])

    # voltage
    for _in in ["in0","in1","in2","in3","in4","in5","in6","in7","in8","in9","in10"]:
        sensor_id = "%s/voltage-%s" % (chip_name,_in)
        value = "\"%s\"" % sensor_id
        keys = _keys + ["Sensor",value]
        dop.cdp_set("collectdplugin",keys,value,multiple_file=True,is_opt_multi=True)
        orders.append([value])

    dop.cdp_set("collectplugin",orders_key,orders,multiple_file=True,is_opt_multi=True)

    # 上記で指定されたものを対象外にする場合はtrue
    keys = _keys + ["IgnoreSelected"]
    value = "false"
    dop.cdp_set("collectdplugin",keys,value,multiple_file=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","sensors"],recursive=True,multiple_file=True)
        dop.cdp_uncomment("collectdplugin",_keys,recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","sensors"],recursive=True,multiple_file=True)
        dop.cdp_comment("collectdplugin",_keys,recursive=True,multiple_file=True)

def enable_sensors_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_sensors_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_sensors_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_sensors_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_uptime_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "uptime"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","uptime"],"uptime",multiple_file=True,is_opt_multi=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","uptime"],recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","uptime"],recursive=True,multiple_file=True)

def enable_uptime_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_uptime_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_uptime_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_uptime_plugin(flag=False, dop=dop, webobj=webobj, host=host)


def switch_users_plugin(flag=True, dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "users"

    dop.cdp_set("collectdplugin",[configName,"LoadPlugin","users"],"users",multiple_file=True,is_opt_multi=True)

    if flag is True:
        dop.cdp_uncomment("collectdplugin",[configName,"LoadPlugin","users"],recursive=True,multiple_file=True)
    else:
        dop.cdp_comment("collectdplugin",[configName,"LoadPlugin","users"],recursive=True,multiple_file=True)

def enable_users_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_users_plugin(flag=True, dop=dop, webobj=webobj, host=host)

def disable_users_plugin(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    switch_users_plugin(flag=False, dop=dop, webobj=webobj, host=host)




def init_filter(dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    configName = "filter"

    load_plugins = ["match_regex","match_value","target_notification"]

    if dop.cdp_isset("collectdplugin",[configName,"@ORDERS"],multiple_file=True) is True:
        orders = dop.get("collectdplugin",[configName,"@ORDERS"])
    else:
        orders = []

    for plugin_name in load_plugins:
        if dop.cdp_isset("collectdplugin",[configName,"LoadPlugin",plugin_name],multiple_file=True) is False:
            dop.cdp_set("collectdplugin",[configName,"LoadPlugin",plugin_name],plugin_name,multiple_file=True,is_opt_multi=True)
            orders.append(["LoadPlugin",plugin_name])

    dop.set("collectdplugin",[configName,"@ORDERS"],orders)

def set_chain_rule(type,chain,rule,params,dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    init_filter(dop, webobj, host)

    configName = "filter"
    _keys = [configName,type,"\"%s\"" % chain]

    if dop.cdp_isset("collectdplugin", _keys, multiple_file=True) is False:
        dop.cdp_set("collectdplugin", _keys, chain, multiple_file=True, is_opt_multi=True)
        dop.cdp_set_pre_comment("collectdplugin", _keys, [''], multiple_file=True)

    _keys = [configName,"Chain",chain]

    try:
        plugin = "\"^%s$\"" % params["Plugin"]
        keys = _keys + ["Rule",rule,"Match","regex","Plugin"]
        dop.cdp_set("collectdplugin", keys, plugin, multiple_file=True)
    except:
        pass

    try:
        type_instance = "\"^%s$\"" % params["TypeInstance"]
        keys = _keys + ["Rule",rule,"Match","regex","TypeInstance"]
        dop.cdp_set("collectdplugin", keys, type_instance, multiple_file=True)
    except:
        pass

    try:
        min = params["Min"]
        keys = _keys + ["Rule",rule,"Match","value","Min"]
        dop.cdp_set("collectdplugin", keys, min, multiple_file=True)
    except:
        pass

    try:
        max = params["Max"]
        keys = _keys + ["Rule",rule,"Match","value","Max"]
        dop.cdp_set("collectdplugin", keys, max, multiple_file=True)
    except:
        pass

    try:
        invert = params["Invert"]
        keys = _keys + ["Rule",rule,"Match","value","Invert"]
        dop.cdp_set("collectdplugin", keys, invert, multiple_file=True)
    except:
        pass

    try:
        satisfy = "\"%s\"" % params["Satisfy"]
        keys = _keys + ["Rule",rule,"Match","value","Satisfy"]
        dop.cdp_set("collectdplugin", keys, satisfy, multiple_file=True)
    except:
        pass

    try:
        if params['Target'] == "notification":
            try:
                message = "\"%s\"" % params["Message"]
                keys = _keys + ["Rule",rule,"Target","notification","Message"]
                dop.cdp_set("collectdplugin", keys, message,multiple_file=True)
            except:
                pass

            try:
                severity = "\"%s\"" % params["Severity"]
                keys = _keys + ["Rule",rule,"Target","notification","Severity"]
                dop.cdp_set("collectdplugin", keys, severity,multiple_file=True)
            except:
                pass

        else:
            try:
                keys = _keys + ["Rule",rule,"Target",params['Target'],"Pass"]
                dop.cdp_set("collectdplugin", keys, "" ,multiple_file=True)
                dop.cdp_comment("collectdplugin", keys, multiple_file=True)
            except:
                pass
    except:
        pass

    #keys = _keys + ["Target"]
    #dop.cdp_set("collectdplugin", keys, "\"write\"", multiple_file=True)

def set_pre_cache_chain_rule(chain,rule,params,dop=None,webobj=None,host=None):
    global DictOp

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    set_chain_rule("PreCacheChain",chain,rule,params,dop,webobj,host)

def set_post_cache_chain_rule(chain,rule,params,dop=None,webobj=None,host=None):
    global DictOp

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    set_chain_rule("PostCacheChain",chain,rule,params,dop,webobj,host)


def create_threshold_config_name(plugin,selector):

    configName = "threshold"

    data = plugin_selector_to_dict(selector)
    config_name = "%s_%s" % (configName,plugin,)
    try:
        config_name += ":%s" % (data['plugin_instance'],)
    except:
        config_name += ":"
    try:
        config_name += ":%s" % (data['type'],)
    except:
        config_name += ":"
    try:
        config_name += ":%s" % (data['type_instance'],)
    except:
        config_name += ":"
    try:
        config_name += ":%s" % (data['ds'],)
    except:
        config_name += ":"
    try:
        config_name += ":%s" % (data['host'],)
    except:
        pass
        #config_name += ":"

    return config_name

def set_threshold(plugin,selector,params,dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    enable_python_plugin(dop=dop, webobj=webobj, host=host)

    config_name = create_threshold_config_name(plugin,selector)

    data = plugin_selector_to_dict(selector)
    try:
        plugin_instance = data['plugin_instance']
    except:
        plugin_instance = None
    try:
        type = data['type']
    except:
        type = None
    try:
        type_instance = data['type_instance']
    except:
        type_instance = None
    try:
        ds = data['ds']
    except:
        ds = None
    try:
        host = data['host']
        _keys = [config_name,"Threshold","","Host",host,"Plugin",plugin]
    except:
        host = None
        _keys = [config_name,"Threshold","","Plugin",plugin]

    if plugin_instance is not None:
        keys = _keys + ["Instance"]
        try:
            int(plugin_instance)
            _plugin_instance = "\"%d\"" % int(plugin_instance)
        except:
            _plugin_instance = plugin_instance
            pass
        dop.cdp_set("collectdplugin", keys, _plugin_instance, multiple_file=True)

    if type is not None:
        _keys = _keys + ["Type",type]

        if type_instance is not None:
            keys = _keys + ["Instance"]
            dop.cdp_set("collectdplugin", keys, "\"%s\"" % type_instance, multiple_file=True)

        if ds is not None:
            keys = _keys + ["DataSource"]
            dop.cdp_set("collectdplugin", keys, "\"%s\"" % ds, multiple_file=True)

        try:
            params['Message']
        except:
            msg_dict = {}
            for _param in ["plugin","plugin_instance","type","type_instance","ds","host"]:
                try:
                    exec("if %s is not None: msg_dict['%s'] = str(%s)" % (_param,_param,_param,))
                    exec("if %s is None: msg_dict['%s'] = '%%{%s}'" % (_param,_param,_param,))
                except:
                    pass

            for _param in ["WarningMax","WarningMin","FailureMax","FailureMin","Percentage","Persist","Hits","Hysteresis"]:
                try:
                    _name = re.sub("([a-z])([A-Z])","\\1_\\2",_param).lower()
                    exec("msg_dict['%s'] = params['%s']" % (_name,_param,))
                except:
                    pass

            params['Message'] = "\"%s\"" % str(msg_dict)


        for _param in ["WarningMax","WarningMin","FailureMax","FailureMin","Percentage","Persist","Hits","Hysteresis","Message"]:
            try:
                param_val = params[_param]
                keys = _keys + [_param]
                dop.cdp_set("collectdplugin", keys, param_val, multiple_file=True)
            except:
                pass

def disable_threshold(plugin,selector,dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    config_name = create_threshold_config_name(plugin,selector)
    keys = [config_name,"Threshold",""]

    dop.cdp_comment("collectdplugin", keys, multiple_file=True)

def enable_threshold(plugin,selector,dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    config_name = create_threshold_config_name(plugin,selector)
    keys = [config_name,"Threshold",""]

    dop.cdp_uncomment("collectdplugin", keys, recursive=True, multiple_file=True)

def delete_threshold(plugin,selector,dop=None, webobj=None, host=None):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    config_name = create_threshold_config_name(plugin,selector)
    keys = [config_name]

    dop.delete("collectdplugin", keys)


def initialize_collectd_settings(dop=None, webobj=None, host=None, force=False, reverse=False):
    global DictOp
    retval = False

    if dop is None:
        if isinstance(DictOp, types.InstanceType) and DictOp.__class__.__name__ == "DictOp":
            dop = DictOp
        else:
            dop = _get_collectd_config(webobj, host)

    # general settings
    if not "collectd" in dop.ModuleNames:
        from karesansui.lib.parser.collectd import collectdParser
        conf_arr =  collectdParser().read_conf()
        dop.addconf("collectd",conf_arr)

    default_params = {
              "Hostname"   :"\"localhost\"",
              "FQDNLookup" :"true",
              "BaseDir"    :"\"%s\"" % COLLECTD_DATA_DIR,
              "PIDFile"    :"\"%s\"" % COLLECTD_PID_FILE,
              "PluginDir"  :"\"%s\"" % COLLECTD_PLUGIN_DIR,
              "TypesDB"    :"\"%s/types.db\"" % COLLECTD_SHARE_DIR,
              "Include"    :"\"%s/*.conf\"" % PARSER_COLLECTD_PLUGIN_DIR,
              "Interval"   :"3",
              "ReadThreads":"5",
              }

    for _k,_v in default_params.iteritems():
        if dop.cdp_isset("collectd",[_k]) is False or force is True:
            # Include行は複数設定可(is_opt_multi)なのでis_opt_multi=Trueでset
            if _k == "Include":
                # 既存Include行を削除
                if dop.cdp_isset("collectd",[_k]) is True:
                    for _k2 in dop.cdp_get("collectd",[_k]).keys():
                        dop.cdp_delete("collectd",[_k,_k2])
                dop.cdp_set("collectd",[_k,_v] ,_v,is_opt_multi=True)
            else:
                dop.cdp_set("collectd",[_k]    ,_v)

    # each plugin settings
    from karesansui.lib.parser.collectdplugin import collectdpluginParser

    # まだ読み込まれていないプラグイン設定ファイルを読み込む
    includes = []
    for _plugin in COLLECTD_PLUGINS:
        if dop.isset("collectdplugin",_plugin) is False:
            includes.append(_plugin)
    if len(includes) != 0:
        extra_args = {"include":"^(%s)$" % "|".join(includes)}
        new_conf_arr =  collectdpluginParser().read_conf(extra_args)
        for _k,_v in new_conf_arr.iteritems():
            if _k[0:1] != "@":
                dop.set("collectdplugin",[_k],_v['value'])

    # コメントを外す
    for _plugin in COLLECTD_PLUGINS:
        if dop.isset("collectdplugin",[_plugin,"LoadPlugin"]) is True:
            loadplugins = dop.get("collectdplugin",[_plugin,"LoadPlugin"])
            for _k,_v in loadplugins.iteritems():
                if _v['comment'] is True:
                    if reverse is True:
                        disabled_plugin(_plugin, dop=dop, webobj=webobj, host=host)
                    else:
                        enabled_plugin(_plugin, dop=dop, webobj=webobj, host=host)

    # pythonプラグインの初期値設定
    if "python" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["python"]) is True:
        if reverse is True:
            disable_python_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_python_plugin(dop=dop, webobj=webobj, host=host)

    # syslogプラグインの初期値設定
    if "syslog" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["syslog"]) is True:
        if reverse is True:
            disable_syslog_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_syslog_plugin(dop=dop, webobj=webobj, host=host)

    # logfileプラグインの初期値設定
    if "logfile" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["logfile"]) is True:
        if reverse is True:
            disable_logfile_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_logfile_plugin(dop=dop, webobj=webobj, host=host)

    # rrdtoolプラグインの初期値設定
    if "rrdtool" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["rrdtool"]) is True:
        if reverse is True:
            disable_rrdtool_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_rrdtool_plugin(dop=dop, webobj=webobj, host=host)

    # rrdcachedプラグインの初期値設定
    if "rrdcached" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["rrdcached"]) is True:
        if reverse is True:
            disable_rrdcached_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_rrdcached_plugin(dop=dop, webobj=webobj, host=host)

    # memoryプラグインの初期値設定
    if "memory" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["memory"]) is True:
        if reverse is True:
            disable_memory_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_memory_plugin(dop=dop, webobj=webobj, host=host)

    # cpuプラグインの初期値設定
    if "cpu" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["cpu"]) is True:
        if reverse is True:
            disable_cpu_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_cpu_plugin(dop=dop, webobj=webobj, host=host)

    # diskプラグインの初期値設定
    if "disk" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["disk"]) is True:
        if reverse is True:
            disable_disk_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_disk_plugin(dop=dop, webobj=webobj, host=host)

    # dfプラグインの初期値設定
    if "df" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["df"]) is True:
        if reverse is True:
            disable_df_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_df_plugin(dop=dop, webobj=webobj, host=host)

    # interfaceプラグインの初期値設定
    if "interface" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["interface"]) is True:
        if reverse is True:
            disable_interface_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_interface_plugin(dop=dop, webobj=webobj, host=host)

    # libvirtプラグインの初期値設定
    if "libvirt" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["libvirt"]) is True:
        if reverse is True:
            disable_libvirt_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_libvirt_plugin(dop=dop, webobj=webobj, host=host)

    # sensorsプラグインの初期値設定
    if "sensors" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["sensors"]) is True:
        if reverse is True:
            disable_sensors_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_sensors_plugin(dop=dop, webobj=webobj, host=host)

    # uptimeプラグインの初期値設定
    if "uptime" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["uptime"]) is True:
        if reverse is True:
            disable_uptime_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_uptime_plugin(dop=dop, webobj=webobj, host=host)

    # usersプラグインの初期値設定
    if "users" in COLLECTD_PLUGINS and dop.isset("collectdplugin",["users"]) is True:
        if reverse is True:
            disable_users_plugin(dop=dop, webobj=webobj, host=host)
        else:
            enable_users_plugin(dop=dop, webobj=webobj, host=host)


"""
"""
if __name__ == '__main__':
    """Testing
    """

    # プラグインのリストを取得
    list = plugin_list()
    preprint_r(list)

    # 有効なプラグインの取得
    list = active_plugin_list(dop=DictOp)
    preprint_r(list)

    # 無効なプラグインの取得
    list = inactive_plugin_list(dop=DictOp)
    preprint_r(list)

    # プラグインが有効かどうか(syslog)
    plugin_name = "syslog"
    print is_enabled_plugin(plugin_name,dop=DictOp)

    # プラグインが有効かどうか(logfile)
    plugin_name = "logfile"
    print is_enabled_plugin(plugin_name,dop=DictOp)

    # プラグインを有効化(iptables)
    plugin_name = "iptables"
    enabled_plugin(plugin_name,dop=DictOp)
    # プラグインが有効かどうか(iptables)
    print is_enabled_plugin(plugin_name,dop=DictOp)

    # プラグインを無効化(logfile)
    plugin_name = "logfile"
    disabled_plugin(plugin_name,dop=DictOp)
    # プラグインが有効かどうか(logfile)
    print is_enabled_plugin(plugin_name,dop=DictOp)

    # Intervalパラメータの取得
    print get_global_parameter("Interval",dop=DictOp)

    # Intervalパラメータの変更
    print set_global_parameter("Interval","23",dop=DictOp)
    # Intervalパラメータの取得
    print get_global_parameter("Interval")

    # ここまでの設定内容を確認（メモリ上）
    #preprint_r(DictOp.getconf("collectdplugin"))

    # プラグイン設定がどのファイルに記述されているか(iptables)
    # xxxx.conf の xxxx の部分が返される
    plugin_name = "iptables"
    print where_is_plugin(plugin_name)

    #################################
    # Filterの設定
    #################################

    # ルールの作成 (ルール名:memory_cached_exceeded)
    # 数値も全て文字列にしてください
    rule_name = "memory_cached_exceeded"
    params = {}
    params['Plugin']   = "memory"
    params['TypeInstance'] = "cached"
    params['Min']      = "97000000"
    #params['Max']     = "1000000000"
    #params['Invert']  = "false"
    params['Satisfy']  = "Any"
    params['Target']   = "notification"
    params['Message']  = "Oops, the %{plugin} %{type_instance} memory_size is currently %{ds:value}!"
    params['Severity'] = "WARNING"
    set_post_cache_chain_rule("PostTestChain",rule_name,params)

    # ルールの作成 (ルール名:memory_used_exceeded)
    # 数値も全て文字列にしてください
    rule_name = "memory_used_exceeded"
    params = {}
    params['Plugin']   = "memory";
    params['TypeInstance'] = "used";
    params['Min']      = "550000000";
    #params['Max']     = "10000000000";
    #params['Invert']  = "false";
    params['Satisfy']  = "Any";
    params['Target']   = "notification";
    params['Message']  = "Oops, the %{plugin} %{type_instance} memory_size is currently %{ds:value}!";
    params['Severity'] = "WARNING";
    set_post_cache_chain_rule("PostTestChain",rule_name,params)

    # ルールの作成 (ルール名:cpu_exceeded)
    # 数値も全て文字列にしてください
    rule_name = "cpu_exceeded"
    params = {}
    params['Plugin']   = "cpu";
    #params['TypeInstance'] = "";
    params['Min']      = "0";
    params['Max']      = "80";
    params['Invert']  = "false";
    params['Satisfy']  = "All";
    params['Target']   = "notification";
    params['Message']  = "Oops, the %{plugin} %{type_instance} cpu is currently %{ds:value}!";
    params['Severity'] = "FAILURE";
    set_post_cache_chain_rule("PostTestChain",rule_name,params)

    ## dict_op の 個別テスト
    #DictOp.unset("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded"],is_cdp=True,multiple_file=True)
    #DictOp.delete("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded","Match"],is_cdp=True,multiple_file=True)
    #DictOp.comment("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded"],is_cdp=True,multiple_file=True)
    #DictOp.uncomment("collectdplugin",["filter","Chain","PostTestChain","Rule","cpub_exceeded"],is_cdp=True,multiple_file=True)
    #print DictOp.action("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded","Match"],is_cdp=True,multiple_file=True)
    print DictOp.unset("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded","Match"],is_cdp=True,multiple_file=True)
    print DictOp.isset("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded","Match"],is_cdp=True,multiple_file=True)
    print DictOp.cdp_isset("collectdplugin",["filter","Chain","PostTestChain","Rule","cpua_exceeded","Match"],multiple_file=True)


    #################################
    # Thresholdの設定
    #################################

    # スレッショルドの作成 (df)
    plugin_name     = "df"
    plugin_instance = None
    type            = "df"
    type_instance   = "boot"
    ds              = "used"

    # 数値も全て文字列にしてください
    selector = create_plugin_selector(plugin_instance, type, type_instance, ds)
    params = {}
    params['WarningMax'] = "10";
    params['FailureMax'] = "25";
    params['Percentage'] = "true";
    params['Persist']    = "true";
    params['Message']    =  "\"name:%{ds:name} val:%{ds:value} fmin:%{failure_min} fmax:%{failure_max} wmin:%{warning_min} wmax:%{warning_max}\""
    set_threshold(plugin_name,selector,params)


    # スレッショルドの作成 (load)
    plugin_name     = "load"
    plugin_instance = None
    type            = "load"
    type_instance   = None
    ds              = "shortterm"

    # 数値も全て文字列にしてください
    selector = create_plugin_selector(plugin_instance, type, type_instance, ds)
    params = {}
    params['WarningMax'] = "0.02";
    params['FailureMax'] = "1.5";
    params['Percentage'] = "false";
    params['Persist']    = "true";
    #params['Message']    =  "\"name:%{ds:name} val:%{ds:value} fmin:%{failure_min} fmax:%{failure_max} wmin:%{warning_min} wmax:%{warning_max}\""
    set_threshold(plugin_name,selector,params)

    # コメントで無効化
    disable_threshold(plugin_name,selector)

    # コメント外しで有効化
    enable_threshold(plugin_name,selector)

    # コメントで無効化
    disable_threshold(plugin_name,selector)

    # pythonプラグインの無効化
    disable_python_plugin()
    # pythonプラグインの有効化
    enable_python_plugin()


    """
    # df,disk,interface,libvirt,load......だけ読み込み
    from karesansui.lib.parser.collectdplugin import collectdpluginParser
    extra_args = {"include":"^(df|disk|interface|libvirt|load|logfile|memory|python|rrdcached|rrdtool|sensors|syslog)$"}
    DictOp.addconf("collectdplugin",collectdpluginParser().read_conf(extra_args=extra_args))
    # 各種プラグイン設定を初期化する(この時点でcpu設定は読み込まれていない)
    initialize_collectd_settings(dop=DictOp)
    """

    # ここまでの設定内容を確認（メモリ上）
    conf = DictOp.getconf("collectdplugin")
    preprint_r(conf)
    #preprint_r(conf["filter"])
    #preprint_r(conf["python"])

    # 設定書き込み（dryrun指定で標準出力のみ）
    from karesansui.lib.parser.collectdplugin import collectdpluginParser
    parser = collectdpluginParser()
    parser.write_conf(conf,dryrun=True)

    print get_collectd_param(param="BaseDir"     , section=None)
    print get_collectd_param(param="DataDir"     , section="rrdtool")
    print get_collectd_param(param="CacheTimeout", section="rrdtool")

    pass
