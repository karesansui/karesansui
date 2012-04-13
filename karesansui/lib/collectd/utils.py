#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

import os, sys, fcntl

import karesansui
from karesansui import KaresansuiLibException

"""
Prepare for using orm (start)
"""
environ = {"KARESANSUI_CONF":"/etc/karesansui/application.conf"}
for _k,_v in environ.iteritems():
    os.environ[_k] = _v

from karesansui.lib.file.k2v import K2V
from karesansui.prep import create__cmd__
config_file = os.environ["KARESANSUI_CONF"]
if config_file: # read file
    _k2v = K2V(config_file)
    config = _k2v.read()

if config and config.has_key('application.search.path'):
    for y in [x.strip() for x in config['application.search.path'].split(',') if x]:
        if (y in sys.path) is False: sys.path.insert(0, y)

create__cmd__(config, config_file)
karesansui.config = config
if not karesansui.config:
    print >>sys.stderr, '[Error] Failed to load configuration file.'
    sys.exit(1)

"""
Prepare for using orm (end)
"""

def get_karesansui_config():
    return karesansui.config

def append_line(filename="/dev/null",string=""):
    try:
        fp = open(filename,"a")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_EX)
        try:
            fp.write("%s\n" % string.encode("utf_8"))
        except:
            fp.write("%s\n" % string)
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
    except:
        raise

def get_collectd_version():
    retval = False

    from karesansui.lib.const import VENDOR_SBIN_DIR
    from karesansui.lib.utils import execute_command

    collectd_command = "%s/collectd" % VENDOR_SBIN_DIR
    command_args = [collectd_command,"-h"]
    (rc,res) = execute_command(command_args)

    for _line in res:
        if _line[0:9] == "collectd ":
            retval = _line.split()[1]
            if retval[-1:] == ",":
                retval = retval[0:-1]
            break

    return retval


def create_plugin_selector(plugin_instance=None, type=None, type_instance=None, ds=None, host=None):
    selector = ""

    if plugin_instance is not None and plugin_instance != "":
        selector = '%splugin_instance:%s,' % (selector, plugin_instance)

    if type is not None and type != "":
        selector = '%stype:%s,' % (selector, type)

    if type_instance is not None and type_instance != "":
        selector = '%stype_instance:%s,' % (selector, type_instance)

    if ds is not None and ds != "":
        selector = '%sds:%s,' % (selector, ds)

    if host is not None and host != "":
        selector = '%shost:%s,' % (selector, host)

    selector = selector.rstrip(',')

    return str(selector)

def plugin_selector_to_dict(selector):
    from karesansui.lib.utils import comma_split
    selector_arr = comma_split(selector)
    selector_dict = dict()

    for select in selector_arr:
        (key, val) = select.split(':',2)
        selector_dict[key] = val

    return selector_dict

def create_threshold_value(min_value=None, max_value=None):
    value = ""

    if min_value is not None and min_value != "":
        value = '%smin:%s,' % (value, min_value)

    if max_value is not None and max_value != "":
        value = '%smax:%s,' % (value, max_value)

    value = value.rstrip(',')
    return value

def threshold_value_to_dict(value):
    from karesansui.lib.utils import comma_split
    value_arr = comma_split(value)
    value_dict = dict()

    for value in value_arr:
        (key, val) = value.split(':',2)
        value_dict[key] = val

    return value_dict

def query_watch_data(plugin,plugin_instance,type,type_instance,ds,host=None):
    import karesansui.db
    kss_engine   = karesansui.db.get_engine()
    kss_metadata = karesansui.db.get_metadata()
    kss_session  = karesansui.db.get_session()

    myhostname = os.uname()[1]
    if host == myhostname:
        host = None

    from karesansui.db.access.watch import    \
        findbyall       as w_findbyall,       \
        findby1         as w_findby1,         \
        findby1name     as w_findby1name,     \
        findbyallplugin as w_findbyallplugin, \
        findbyand       as w_findbyand

    retval = []

    plugin_selector = create_plugin_selector(plugin_instance,type,type_instance,ds,host)
    try:
        watchs = w_findbyallplugin(kss_session,plugin)
        for watch in watchs:
            if str(plugin_selector) == str(watch.plugin_selector):
                name  = watch.name

                check_continuation = watch.continuation_count
                check_span         = watch.prohibition_period

                warning_value     = threshold_value_to_dict(watch.warning_value)
                warning_script    = watch.warning_script
                warning_mail_body = watch.warning_mail_body
                is_warning_percentage = watch.is_warning_percentage
                is_warning_script     = watch.is_warning_script
                is_warning_mail       = watch.is_warning_mail

                failure_value     = threshold_value_to_dict(watch.failure_value)
                failure_script    = watch.failure_script
                failure_mail_body = watch.failure_mail_body
                is_failure_percentage = watch.is_failure_percentage
                is_failure_script     = watch.is_failure_script
                is_failure_mail       = watch.is_failure_mail

                okay_script    = watch.okay_script
                okay_mail_body = watch.okay_mail_body
                is_okay_script = watch.is_okay_script
                is_okay_mail   = watch.is_okay_mail

                notify_mail_from  = watch.notify_mail_from
                notify_mail_to    = watch.notify_mail_to

                data = {"name"                  :name,
                        "check_continuation"    :check_continuation,
                        "check_span"            :check_span,
                        "warning_value"         :warning_value,
                        "warning_script"        :warning_script,
                        "warning_mail_body"     :warning_mail_body,
                        "is_warning_percentage" :is_warning_percentage,
                        "is_warning_script"     :is_warning_script,
                        "is_warning_mail"       :is_warning_mail,
                        "failure_value"         :failure_value,
                        "failure_script"        :failure_script,
                        "failure_mail_body"     :failure_mail_body,
                        "is_failure_percentage" :is_failure_percentage,
                        "is_failure_script"     :is_failure_script,
                        "is_failure_mail"       :is_failure_mail,
                        "okay_script"           :okay_script,
                        "okay_mail_body"        :okay_mail_body,
                        "is_okay_script"        :is_okay_script,
                        "is_okay_mail"          :is_okay_mail,
                        "notify_mail_from"      :notify_mail_from,
                        "notify_mail_to"        :notify_mail_to,
                        }
                retval.append(data)
    except:
        pass

    return retval


def evaluate_macro(string,macros={}):
    from karesansui.lib.utils import array_replace

    lines = string.split("\n")

    pattern = []
    replace = []
    for _k,_v in macros.iteritems():
        pattern.append("%%{%s}" % _k)
        replace.append(str(_v))

    """
    ff = open("/tmp/replace-debug.log","a")
    ff.write(str(pattern)+"\n")
    ff.write(str(replace)+"\n")
    ff.close()
    """
    return "\n".join(array_replace(lines,pattern,replace,mode="g"))



if __name__ == '__main__':

    watch_column = [ 'name',
                     'check_continuation',
                     'check_span',
                     'warning_value',
                     'warning_script',
                     'warning_mail_body',
                     'is_warning_percentage',
                     'is_warning_script',
                     'is_warning_mail',
                     'failure_value',
                     'failure_script',
                     'failure_mail_body',
                     'is_failure_percentage',
                     'is_failure_script',
                     'is_failure_mail',
                     'okay_script',
                     'okay_mail_body',
                     'is_okay_script',
                     'is_okay_mail',
                     'notify_mail_from',
                     'notify_mail_to']

    plugin          = "cpu"
    plugin_instance = "0"
    type            = "cpu"
    type_instance   = "user"
    ds              = "value"
    host            = None
    host            = "foo.example.com"

    from karesansui.lib.utils import preprint_r
    watch_data = query_watch_data(plugin,plugin_instance,type,type_instance,ds,host=host)
    preprint_r(watch_data)
    try:
        for column_name in watch_column:
            exec("%s = watch_data[0]['%s']" % (column_name,column_name,))
            exec("_var = %s" % (column_name,))
            print "%s: %s"  % (column_name,_var)

        macros = {"host":"localhost.localdomain"}
        print evaluate_macro(okay_mail_body,macros)
    except:
        print "Error: cannot get watch data."
        sys.exit(0)

    pass 
