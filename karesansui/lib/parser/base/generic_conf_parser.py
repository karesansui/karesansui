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

import os
import re
import sys

from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.dict_op import DictOp

"""
Use for parsing files that is written in format such as modprobe.conf etc...
"""

class genericConfParser:

    _delim               = " "
    _new_delim           = " "
    _comment             = "#"
    _reserved_key_prefix = "@"
    _multi_param         = False

    _module      = "generic_conf_parser"

    def __init__(self,paths=[]):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})
        self.set_source_file(paths)

    def set_delim(self, delim=" "):
        self._delim = delim

    def set_new_delim(self, delim=" "):
        self._new_delim = delim

    def set_comment(self, comment="#"):
        self._comment = comment

    def set_reserved_key_prefix(self, prefix="@"):
        self._reserved_key_prefix = prefix

    def set_source_file(self,paths=[]):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths
        return True

    def get_source_file(self):
        return self.paths

    def source_file(self):
        return self.get_source_file()

    def read_conf(self):
        retval = {}

        for _afile in self.source_file():
            res = ConfigFile(_afile).read()

            regex_str = "^(?P<comment>%s)?[ \t]*(?P<key>[^%s]+)[ \t]*%s[ \t]*(?P<value>.*)$" % (self._comment,self._delim,self._delim,)

            orders    = []
            for _aline in res:
                _aline = _aline.rstrip('\r\n')

                regex = re.compile(r"%s" % regex_str)

                m = regex.match(_aline)
                if m:
                    comment = m.group('comment')
                    key     = m.group('key')
                    value   = m.group('value')

                    pieces = re.split("[ \t]*%s[ \t]*" % (self._delim),value,1)

                    if not value.rfind(self._comment) == -1:
                        value = value[:value.rfind(self._comment)]

                    if len(pieces) == 2 and pieces[1] != "":
                        keys = [_afile,key,pieces[0]]
                        new_value = pieces[1]
                    else:
                        if self._multi_param is True:
                            keys = [_afile,key]
                            if self.dop.isset(self._module,keys):
                                old = self.dop.get(self._module,keys)
                                new_value = old + [value]
                            else:
                                new_value = [value]
                        else:
                            keys = [_afile,key,pieces[0]]
                            new_value = ""

                    self.dop.set(self._module,keys,new_value)
                    if not key in orders:
                        orders.append(key)

                    if comment is not None:
                        self.dop.comment(self._module,keys)

            orders_key = "%sORDERS" % (self._reserved_key_prefix,)
            self.dop.set(self._module,[_afile,orders_key],orders)

        #self.dop.preprint_r(self._module)
        return self.dop.getconf(self._module)


    def _value_to_lines(self,value):
        lines = []

        for _k,_v in value.iteritems():

            try:
                if _v['action'] == "delete":
                    continue
            except:
                pass

            try:
                val = _v['value']

                comment = False
                try:
                    if _v['comment'] is True:
                        comment = True
                except:
                    pass

                if type(val) == list:
                    for _val in val:
                        aline = "%s%s%s" % (_k,self._new_delim,_val,)
                        if comment is True:
                            aline = "%s%s" % (self._comment,aline,)
                        lines.append(aline)
                elif type(val) == dict:
                    for _key in sorted(val.keys()):
                        _val = val[_key]

                        """
                    for _key,_val in val.iteritems():
                        """

                        try:
                            if _val['action'] == "delete":
                                continue
                        except:
                            pass

                        _comment = False
                        try:
                            if _val['comment'] is True:
                                _comment = True
                        except:
                            pass

                        if _val['value'] == "":
                            aline = "%s%s%s" % (_k,self._new_delim,_key,)
                        else:
                            aline = "%s%s%s%s%s" % (_k,self._new_delim,_key,self._new_delim,_val['value'],)
                        if comment is True or _comment is True:
                            aline = "%s%s" % (self._comment,aline,)
                        lines.append(aline)
                else:
                    aline = "%s%s%s" % (_k,self._new_delim,val,)
                    lines.append(aline)

            except:
                pass

        return lines

    def write_conf(self,conf_arr={},dryrun=False):
        retval = True

        self.dop.addconf(self._module,conf_arr)
        orders_key = "%sORDERS" % (self._reserved_key_prefix,)

        for _path,_v in conf_arr.iteritems():

            if _path[0:1] != "/":
                continue

            lines = []
            try:
                _v['value']
            except:
                continue

            exclude_regex = "^%s[A-Z0-9\_]+$" % self._reserved_key_prefix

            # まずはオーダの順
            if self.dop.isset(self._module,[_path,orders_key]) is True:
                for _k2 in self.dop.get(self._module,[_path,orders_key]):
                    m = re.match(exclude_regex,_k2)
                    if not m:
                        try:
                            value = {}
                            value[_k2] = _v['value'][_k2]
                            lines = lines + self._value_to_lines(value)
                            self.dop.unset(self._module,[_path,_k2])
                        except:
                            pass

            # オーダにないものは最後に追加
            for _k2,_v2 in self.dop.get(self._module,[_path]).iteritems():
                m = re.match(exclude_regex,_k2)
                if not m:
                    try:
                        value = {}
                        value[_k2] = _v2
                        lines = lines + self._value_to_lines(value)
                    except:
                        pass

            if dryrun is False:
                if len(lines) > 0:
                    ConfigFile(_path).write("\n".join(lines) + "\n")
                if len(lines) == 0:
                    ConfigFile(_path).write("")
            else:
                if len(lines) > 0:
                    print "\n".join(lines)
                if len(lines) == 0:
                    print ""

        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """
    pass
