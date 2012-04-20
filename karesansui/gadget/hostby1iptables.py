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

import os
import sys
import re
import time
import web

from karesansui.lib.rest import Rest, auth
from karesansui.db.access.machine import findbyhost1
from karesansui.lib.utils import get_ifconfig_info, dict_ksort, is_param
from karesansui.lib.conf import read_conf, write_conf
from karesansui.lib.iptables import iptables_lint_contents

from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID

def validates_iptables_save(obj, host):
    checker = Checker() 
    check = True

    _ = obj._
    checker.errors = []
    
    if not is_param(obj.input, 'iptables_save'):
        check = False
        checker.add_error(_('"%s" is required.') % _('Rule'))
    else:

        check = checker.check_string(
                _('Rule'),
                obj.input.iptables_save,
                CHECK_EMPTY | CHECK_VALID,
                '[^-a-zA-Z0-9_\,\.\@\$\%\!\#\*\[\]\:\/\r\n\+ ]+',
                None,
                None,
            ) and check

        if check is True:
            ret = iptables_lint_contents(obj.input.iptables_save, obj, host)
            if str(ret) != "":
                check = False
                checker.add_error(ret)
                """
                m = re.match(".* line (?P<line>[0-9]+).*",str(ret))
                if m:
                    checker.add_error("LINE:"+m.group("line"))
                """

    obj.view.alert = checker.errors

    return check


class HostBy1Iptables(Rest):

    @auth
    def _GET(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        self.view.host_id = host_id
        self.view.current = get_ifconfig_info()

        modules = ["iptables"]

        host = findbyhost1(self.orm, host_id)
        dop = read_conf(modules, self, host)
        if dop is False:
            return web.internalerror('Internal Server Error. (Timeout)')

        config = dop.get("iptables",["config"])
        status = dop.get("iptables",["status"])
        lint   = dop.get("iptables",["lint"])

        policies = {}
        for _aline in status:
            m = re.match("\*(?P<table>[a-z]+)",_aline.rstrip())
            if m:
                table = m.group("table")
                policies[table] = {}
            else:
                m = re.match(":(?P<chain>[A-Z]+) +(?P<policy>[A-Z]+)",_aline.rstrip())
                if m:
                    chain  = m.group("chain")
                    policy = m.group("policy")
                    policies[table][chain] = policy

        self.view.config   = "\n".join(config)
        self.view.status   = "\n".join(status)
        self.view.lint     = lint
        self.view.policies = policies
        self.view.result_js  = ""

        return True

    @auth
    def _PUT(self, *param, **params):
        host_id = self.chk_hostby1(param)
        if host_id is None: return web.notfound()

        host = findbyhost1(self.orm, host_id)
        if not validates_iptables_save(self, host):
            return web.badrequest(self.view.alert)

        from karesansui.lib.dict_op import DictOp
        dop = DictOp()
        dop.addconf("iptables", {})
        dop.set("iptables",["config"],self.input.iptables_save.split("\r\n"))
        retval = write_conf(dop, self, host)
        if retval is False:
            return web.internalerror('Internal Server Error. (Adding Task)')

        return web.accepted(url=web.ctx.path)


urls = (
    '/host/(\d+)/iptables/?(\.part)$', HostBy1Iptables,
    )
