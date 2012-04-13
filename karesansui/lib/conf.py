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

import os
import sys
import time
import types

import karesansui

from karesansui.lib.const import KARESANSUI_PREFIX, KARESANSUI_DATA_DIR, \
                                 KARESANSUI_USER, KARESANSUI_GROUP, \
                                 CONFIGURE_COMMAND_READ, CONFIGURE_COMMAND_WRITE
from karesansui.lib.dict_op import DictOp
from karesansui.lib.utils import preprint_r, r_chmod, r_chown, r_chgrp, base64_encode

CONF_TMP_DIR = "%s/tmp/.conf" % (KARESANSUI_DATA_DIR,)

def read_conf(modules, webobj=None, machine=None, extra_args={}):
    """<comment-ja>
    設定ファイルパーサー（モジュール）により設定ファイルの内容を
    辞書配列操作クラスに渡し、そのオブジェクトを返す
    @param modules: モジュールのリスト配列
    @param webobj: 
    @param machine: 
    @type modules: list
    @rtype: object dict_op
    @return: 辞書配列操作オブジェクト
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    if type(modules) == str:
        modules = [modules]

    options = {"module" : ":".join(modules)}

    try:
        options['include'] = extra_args['include']
    except:
        pass

    #cmd_name = u"Get Settings - %s" % ":".join(modules)
    cmd_name = u"Get Settings"

    if type(webobj) == types.InstanceType:
        from karesansui.db.model._2pysilhouette import Job, JobGroup, \
                                                       JOBGROUP_TYPE
        from karesansui.db.access._2pysilhouette import jg_findby1, jg_save,corp
        from karesansui.db.access._2pysilhouette import save_job_collaboration
        from karesansui.db.access.machine2jobgroup import new as m2j_new
        from pysilhouette.command import dict2command

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'],
                       CONFIGURE_COMMAND_READ), options)

        jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])
        jobgroup.jobs.append(Job('%s command' % cmd_name, 0, _cmd))
        jobgroup.type = JOBGROUP_TYPE['PARALLEL']

        _machine2jobgroup = m2j_new(machine=machine,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=webobj.me,
                                modified_user=webobj.me,
                                )

        if corp(webobj.orm, webobj.pysilhouette.orm,_machine2jobgroup, jobgroup) is False:
            webobj.logger.debug("%s command failed. Return to timeout" % (cmd_name))
            return False

        cmd_res = jobgroup.jobs[0].action_stdout

    else:
        from karesansui.lib.utils import execute_command

        opts_str = ""
        for x in options.keys():
            if options[x] is None:
                opts_str += "--%s " % x 
            else:
                opts_str += "--%s=%s " % (x, options[x])

        _cmd = "%s/bin/%s %s" % (KARESANSUI_PREFIX, CONFIGURE_COMMAND_READ, opts_str.strip(),)

        command_args = _cmd.strip().split(" ")
        (rc,res) = execute_command(command_args)
        if rc != 0:
            return False

        cmd_res = "\n".join(res)

    dop = DictOp()
    try:
        exec(cmd_res)
    except Exception:
        return False

    for module in modules:
        try:
            exec("dop.addconf('%s',Config_Dict_%s)" % (module,module,))
        except:
            pass

    return dop

def write_conf(dop, webobj=None, machine=None, modules=[], extra_args={}):
    """<comment-ja>
    @param dop: 辞書配列操作オブジェクト
    @param webobj: 
    @param machine: 
    @type dop: object dict_op
    @rtype: boolean
    @return: True or False
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from karesansui.lib.file.configfile import ConfigFile

    if isinstance(dop,karesansui.lib.dict_op.DictOp) is False:
        return False

    if not os.path.exists(CONF_TMP_DIR):
        os.makedirs(CONF_TMP_DIR)
        r_chmod(CONF_TMP_DIR,0770)
        r_chown(CONF_TMP_DIR,KARESANSUI_USER)
        r_chgrp(CONF_TMP_DIR,KARESANSUI_GROUP)

    serial = time.strftime("%Y%m%d%H%M%S",time.localtime())

    if len(modules) == 0:
        modules = dop.ModuleNames

    w_modules = []
    w_files   = []
    for _module in modules:
        if _module in dop.ModuleNames:
            filename = "%s/%s.%s" % (CONF_TMP_DIR,_module,serial,)
            data = preprint_r(dop.getconf(_module),return_var=True)
            ConfigFile(filename).write(data+"\n")
            r_chmod(filename,0660)
            r_chown(filename,KARESANSUI_USER)
            r_chgrp(filename,KARESANSUI_GROUP)
            w_modules.append(_module)
            w_files.append(filename)

    if len(w_modules) == 0:
        return False

    options = {
         "module"     : ":".join(w_modules),
         "input-file" : ":".join(w_files),
    }
    options["delete"] = None

    try:
        extra_args['pre-command']
        options['pre-command'] = "b64:" + base64_encode(extra_args['pre-command'])
    except:
        pass
    try:
        extra_args['post-command']
        options['post-command'] = "b64:" + base64_encode(extra_args['post-command'])
    except:
        pass

    try:
        options['include'] = extra_args['include']
    except:
        pass

    #cmd_name = u"Write Settings - %s" % ":".join(w_modules)
    cmd_name = u"Write Settings"

    if type(webobj) == types.InstanceType:
        from karesansui.db.model._2pysilhouette import Job, JobGroup, \
                                                       JOBGROUP_TYPE
        from karesansui.db.access._2pysilhouette import jg_findby1, jg_save,corp
        from karesansui.db.access._2pysilhouette import save_job_collaboration
        from karesansui.db.access.machine2jobgroup import new as m2j_new
        from pysilhouette.command import dict2command

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'],
                       CONFIGURE_COMMAND_WRITE), options)

        _jobgroup = JobGroup(cmd_name, karesansui.sheconf['env.uniqkey'])
        _jobgroup.jobs.append(Job('%s command' % cmd_name, 0, _cmd))

        _machine2jobgroup = m2j_new(machine=machine,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=webobj.me,
                                modified_user=webobj.me,
                                )

        save_job_collaboration(webobj.orm,
                               webobj.pysilhouette.orm,
                               _machine2jobgroup,
                               _jobgroup,
                               )

        """
        _jobgroup.type = JOBGROUP_TYPE['PARALLEL']
        if corp(webobj.orm, webobj.pysilhouette.orm,_machine2jobgroup, _jobgroup) is False:
            webobj.logger.debug("%s command failed. Return to timeout" % (cmd_name))
            for filename in w_files:
                if os.path.exists(filename):
                    os.unlink(filename)
            return False

        cmd_res = jobgroup.jobs[0].action_stdout
        """

    else:
        from karesansui.lib.utils import execute_command

        opts_str = ""
        for x in options.keys():
            if options[x] is None:
                opts_str += "--%s " % x 
            else:
                opts_str += "--%s=%s " % (x, options[x])

        _cmd = "%s/bin/%s %s" % (KARESANSUI_PREFIX, CONFIGURE_COMMAND_WRITE, opts_str.strip(),)

        command_args = _cmd.strip().split(" ")
        (rc,res) = execute_command(command_args)
        if rc != 0:
            for filename in w_files:
                if os.path.exists(filename):
                    os.unlink(filename)
            return False

        cmd_res = "\n".join(res)

    """
    for filename in w_files:
        if os.path.exists(filename):
            os.unlink(filename)
    """

    return True

if __name__ == '__main__':
    """Testing
    """
    modules = ["ifcfg","resolv"]
    dop = read_conf(modules)

    ipaddr = dop.get("ifcfg",["eth0","IPADDR"])
    print ipaddr

    nameservers = dop.get("resolv",["nameserver"])
    if not "127.0.0.1" in nameservers:
        nameservers.append("127.0.0.1")
    dop.set("resolv",["nameserver"],nameservers)

    write_conf(dop)
    pass
