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
import sys
import types
import time
import glob

import karesansui
from karesansui.lib.utils import preprint_r, r_chmod, r_chown, r_chgrp
from karesansui.lib.const import KARESANSUI_PREFIX, KARESANSUI_DATA_DIR, \
                                 KARESANSUI_USER, KARESANSUI_GROUP

CONF_TMP_DIR = "%s/tmp/.conf" % (KARESANSUI_DATA_DIR,)

def iptables_lint_contents(contents, webobj=None, machine=None):
    from karesansui.lib.file.configfile import ConfigFile
    
    if not os.path.exists(CONF_TMP_DIR):
        os.makedirs(CONF_TMP_DIR)
        r_chmod(CONF_TMP_DIR,0770)
        r_chown(CONF_TMP_DIR,KARESANSUI_USER)
        r_chgrp(CONF_TMP_DIR,KARESANSUI_GROUP)

    seconds = 10 * 60
    for _old in glob.glob("%s/iptables-save.*" % (CONF_TMP_DIR,)):
        mtime = os.stat(_old).st_mtime
        if int(time.time()) > (mtime + seconds):
            os.unlink(_old)

    serial = time.strftime("%Y%m%d%H%M%S",time.localtime())
    filename = "%s/iptables-save.%s" % (CONF_TMP_DIR,serial,)

    ConfigFile(filename).write(contents)
    r_chmod(filename,0660)
    r_chown(filename,KARESANSUI_USER)
    r_chgrp(filename,KARESANSUI_GROUP)

    return iptables_lint(filename, webobj, machine, delete=True)

def iptables_lint(filepath, webobj=None, machine=None, delete=False):
    from karesansui.lib.const import IPTABLES_COMMAND_CONTROL

    options = {"config" : filepath, "lint" : None}

    cmd_name = u"Check iptables settings - %s" % filepath

    if type(webobj) == types.InstanceType:
        from karesansui.db.model._2pysilhouette import Job, JobGroup, \
                                                       JOBGROUP_TYPE
        from karesansui.db.access._2pysilhouette import jg_findby1, jg_save,corp
        from karesansui.db.access._2pysilhouette import save_job_collaboration
        from karesansui.db.access.machine2jobgroup import new as m2j_new
        from pysilhouette.command import dict2command

        _cmd = dict2command(
            "%s/%s" % (karesansui.config['application.bin.dir'],
                       IPTABLES_COMMAND_CONTROL), options)

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
            if delete is True and os.path.exists(filepath):
                os.unlink(filepath)
            return False

        cmd_res = jobgroup.jobs[0].action_stdout

    else:
        from karesansui.lib.const import KARESANSUI_PREFIX
        from karesansui.lib.utils import execute_command

        opts_str = ""
        for x in options.keys():
            if options[x] is None:
                opts_str += "--%s " % x 
            else:
                opts_str += "--%s=%s " % (x, options[x])

        _cmd = "%s/bin/%s %s" % (KARESANSUI_PREFIX, IPTABLES_COMMAND_CONTROL, opts_str.strip(),)

        command_args = _cmd.strip().split(" ")
        (rc,res) = execute_command(command_args)
        if rc != 0:
            if delete is True and os.path.exists(filepath):
                os.unlink(filepath)
            return False

        cmd_res = "\n".join(res)


    if delete is True and os.path.exists(filepath):
        os.unlink(filepath)

    return cmd_res

