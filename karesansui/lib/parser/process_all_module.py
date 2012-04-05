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

from karesansui.lib.dict_op import *
from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.utils import execute_command

save_path = "/tmp"
command_read_conf  = "/usr/share/karesansui/bin/read_conf.py"
command_write_conf = "/usr/share/karesansui/bin/write_conf.py"

once_execute = False # コマンド毎回
once_execute = True  # コマンド一回

use_read_conf = True

for _mod in ['ifcfg','network','resolv']:

    print _("################################")
    print _("Processing module '%s'... ") % (_mod)
    print _("################################")

    dop = DictOp()
    try:
        exec("from karesansui.lib.parser.%s  import %sParser as Parser" % (_mod,_mod,))
    except:
        raise

    parser = Parser()

    source_file = parser.source_file()
    print ">" + _("Detecting configuration files")
    print "\n".join(source_file)
    print "<" + _("Detecting configuration files")

    output_file = "%s/%s_dict.py" % (save_path,_mod,)
    if use_read_conf is True:
        command_args = []
        command_args.append(command_read_conf)
        command_args.append("--module")
        command_args.append(_mod)
        command_args.append("--file")
        command_args.append(output_file)
        print ">" + _("Reading configuration files")
        print ">>" + _("Execute") + "=>" + " ".join(command_args)
        (ret, res) = execute_command(command_args)
        if len(res) > 0:
            print ">>" + _("Execute Result") + "=>\n" + "\n".join(res)
        print "<" + _("Reading configuration files")

    else:
        print ">" + _("Reading configuration files")
        dop.addconf(_mod,parser.read_conf())
        print "<" + _("Reading configuration files")

        print ">" + _("Writing module dict files")
        conf = dop.getconf(_mod)
        ConfigFile(output_file).write(str(conf))
        print "<" + _("Writing module dict files")

    if os.path.exists(output_file):
        print ">>Wrote %s" % output_file

        if once_execute is False:
            command_args = []
            command_args.append(command_write_conf)
            command_args.append("--module")
            command_args.append(_mod)
            command_args.append("--file")
            command_args.append(output_file)
            print ">" + _("Writing configuration files")
            print ">>" + _("Execute") + "=>" + " ".join(command_args)
            (ret, res) = execute_command(command_args)
            if len(res) > 0:
                print ">>" + _("Execute Result") + "=>\n" + "\n".join(res)
            print "<" + _("Writing configuration files")

        else:
            try:
                module_args
            except:
                module_args = []
            module_args.append(_mod)
            try:
                file_args
            except:
                file_args = []
            file_args.append(output_file)

if once_execute is True:
    command_args = []
    command_args.append(command_write_conf)
    command_args.append("--module")
    command_args.append(":".join(module_args))
    command_args.append("--file")
    command_args.append(":".join(file_args))
    print ">" + _("Writing configuration files")
    print ">>" + _("Execute") + "=>" + " ".join(command_args)
    (ret, res) = execute_command(command_args)
    if len(res) > 0:
        print ">>" + _("Execute Result") + "=>\n" + "\n".join(res)
    print "<" + _("Writing configuration files")


