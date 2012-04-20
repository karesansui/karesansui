#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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
import re
import sys

from karesansui.lib.utils import preprint_r

"""
try:
    import odict
    Dict = odict.odict()
except:
    Dict = {}
"""

class DictOp:

    def __init__(self):

        self.ModuleNames = []
        self.ConfigArray = {}
        self.set_order_key()

    def set_order_key(self, string="@ORDERS"):
        self.orders_key = string

    def preprint_r(self, module, key=None ,indent=2,depth=None):
        import pprint
        pp = pprint.PrettyPrinter(indent=indent,depth=depth)
        if key is None:
            pp.pprint(self.getconf(module))
        else:
            pp.pprint(self.get(module,key))

    def addconf(self, module, conf_array={}):
        self.ModuleNames.append(module)
        self.ConfigArray[module] = conf_array
        return True

    def getconf(self, module):
        try:
            return self.ConfigArray[module]
        except:
            return {}

    def set(self, module, key, value, is_cdp=False, multiple_file=False):
        return self._set(module,key,value,action='set',is_cdp=is_cdp,multiple_file=multiple_file)

    def add(self, module, key, value, is_cdp=False, multiple_file=False):
        return self._set(module,key,value,action='add',is_cdp=is_cdp,multiple_file=multiple_file)

    def _set(self, module, key, value, action='set', is_cdp=False, multiple_file=False):

        try:
            self.ConfigArray[module]
        except:
            return False

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return False

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str  = "conf"
            cnt = 0
            for _k in key:
                _k = _k.replace("'","\\'")
                eval_str  = "%s['%s']" % (eval_str,_k,)
                try:
                    exec("%s" % (eval_str,))
                    try:
                        exec("%s['action'] = '%s'" % (eval_str,str(action)))
                    except:
                        pass
                except:
                    val_str = "{'value':{},'action':action,'comment':False}"
                    exec("%s = %s" % (eval_str,val_str))

                eval_str  = "%s['value']" % (eval_str,)
                try:
                    exec("%s" % (eval_str,))
                except:
                    val_str = "{}"
                    exec("%s = %s" % (eval_str,val_str))

            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            eval_str_value = "%s['value']" % eval_str

            #print "%s = value" % (eval_str_value,)
            exec("%s = value" % (eval_str_value,))

            self.ConfigArray[module] = conf

        else:
            k_len = len(new_key)
            is_dict = True
            eval_str_value  = "conf"

            if multiple_file is True:
                file_name = new_key.pop(0)
                eval_str         = eval_str_value + "['%s']" % file_name
                eval_str_value  += "['%s']['value']" % file_name
                try:
                    exec("%s" % (eval_str_value,))
                except:
                    try:
                        exec("%s" % (eval_str,))
                    except:
                        val_str = "{}"
                        exec("%s = %s" % (eval_str,val_str))
                    val_str = "{}"
                    exec("%s = %s" % (eval_str_value,val_str))

            cnt = 0
            for _k in new_key:
                eval_str_value  += "['%s']" % _k
                try:
                    exec("%s" % (eval_str_value,))
                except:
                    val_str = "{}"
                    exec("%s = %s" % (eval_str_value,val_str))

                eval_str_value_base  = eval_str_value
                eval_str_value  += "['value']"
                try:
                    exec("%s" % (eval_str_value,))
                except:
                    if is_dict is False:
                        val_str = "{'value':[{},[[],None]],'action':action,'comment':False}"
                    else:
                        val_str = "{'value':{},'action':action,'comment':False}"
                    exec("%s = %s" % (eval_str_value_base,val_str))

                if is_dict is False:
                    eval_str_value  += "[0]"
                    if cnt == k_len:
                        exec("%s = value" % (eval_str_value,))

                is_dict = not is_dict
                cnt = cnt + 1

            exec("%s = value" % (eval_str_value,))
            self.ConfigArray[module] = conf

        return True

    def unset(self, module, key, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return False

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)

            try:
                exec("del %s" % (eval_str,))
                return True
            except:
                return retval

        else:
            is_dict = True
            eval_str  = "conf"

            if multiple_file is True:
                eval_str  += "['%s']['value']" % new_key.pop(0)

            k_len = len(new_key)

            cnt = 0
            for _k in new_key:
                cnt = cnt + 1
                eval_str  += "['%s']" % _k
                if cnt == k_len:
                    break
                eval_str  += "['value']"
                if is_dict is False:
                    eval_str  += "[0]"
                is_dict = not is_dict

            try:
                exec("del %s" % (eval_str,))
                return True
            except:
                return retval


    def get(self, module, key, with_attr=False, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return retval

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            if with_attr is True:
                eval_str_value = "%s" % eval_str
            else:
                eval_str_value = "%s['value']" % eval_str

            try:
                exec("retval = %s" % (eval_str_value,))
                return retval
            except:
                return retval

        else:
            cnt = 0
            k_len = len(new_key)
            is_dict = True
            eval_str_value  = "conf"

            if multiple_file is True:
                eval_str_value  += "['%s']['value']" % new_key.pop(0)

            for _k in new_key:
                eval_str_value  += "['%s']" % _k
                cnt = cnt + 1
                if cnt < k_len:
                    eval_str_value  += "['value']"
                elif cnt == k_len:
                    if with_attr is False:
                        eval_str_value  += "['value']"
                if is_dict is False:
                    eval_str_value  += "[0]"
                is_dict = not is_dict

            try:
                exec("retval = %s" % (eval_str_value,))
                return retval
            except:
                return retval


    def delete(self, module, key, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return retval

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            eval_str_value = "%s['value']" % eval_str

            try:
                exec("%s" % (eval_str,))
                eval_str_action = "%s['action']" % eval_str
                exec("%s = 'delete'" % (eval_str_action,))
            except:
                pass

            self.ConfigArray[module] = conf

        else:
            is_dict = True
            eval_str  = "conf"

            if multiple_file is True:
                eval_str  += "['%s']['value']" % new_key.pop(0)

            k_len = len(new_key)
            cnt = 0
            for _k in new_key:
                cnt = cnt + 1
                eval_str  += "['%s']" % _k
                if cnt == k_len:
                    break
                eval_str  += "['value']"
                if is_dict is False:
                    eval_str  += "[0]"
                is_dict = not is_dict

            try:
                exec("%s" % (eval_str,))
                eval_str_action = "%s['action']" % eval_str
                exec("%s = 'delete'" % (eval_str_action,))
            except:
                pass

            self.ConfigArray[module] = conf

        return True

    def comment(self, module,   key, recursive=False, is_cdp=False, multiple_file=False):
        return self._comment(module,key,flag=True, recursive=recursive,is_cdp=is_cdp,multiple_file=multiple_file)

    def uncomment(self, module, key, recursive=False, is_cdp=False, multiple_file=False):
        return self._comment(module,key,flag=False,recursive=recursive,is_cdp=is_cdp,multiple_file=multiple_file)

    def _comment(self, module, key, flag=True, recursive=False, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return retval

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            eval_str_value = "%s['value']" % eval_str

            try:
                exec("%s" % (eval_str,))
                eval_str_comment = "%s['comment']" % eval_str
                exec("%s = flag" % (eval_str_comment,))
            except:
                pass

            self.ConfigArray[module] = conf

        else:
            is_dict = True
            eval_str  = "conf"

            if multiple_file is True:
                eval_str  += "['%s']['value']" % new_key.pop(0)

            k_len = len(new_key)
            cnt = 0
            for _k in new_key:
                cnt = cnt + 1
                eval_str  += "['%s']" % _k
                if cnt == k_len:
                    break
                eval_str  += "['value']"
                if is_dict is False:
                    eval_str  += "[0]"
                is_dict = not is_dict

            try:
                exec("%s" % (eval_str,))
                eval_str_comment = "%s['comment']" % eval_str
                exec("%s = %s" % (eval_str_comment,str(flag),))

                if recursive is True:
                    eval_str_value = "%s['value']" % eval_str
                    exec("_value = %s" % (eval_str_value,))
                    if type(_value) == list:
                        for _value2 in _value:
                            if type(_value2) == dict:
                                for _k2,_v2 in _value2.iteritems():
                                    r_key = key + [_k2]
                                    self._comment(module, r_key, flag, recursive, is_cdp, multiple_file)
                    elif type(_value) == dict:
                        for _k2,_v2 in _value.iteritems():
                            r_key = key + [_k2]
                            self._comment(module, r_key, flag, recursive, is_cdp, multiple_file)

            except:
                pass

            self.ConfigArray[module] = conf

        return True

    def forceset(self, module, key, value, is_cdp=False, multiple_file=False):
        retval1 = self._set(module,key,value,action='set',is_cdp=is_cdp,multiple_file=multiple_file)
        retval2 = self._comment(module,key,value,flag=False)
        return retval1 & retval2

    def query(self, module, key, regex=".*"):
        retval = self.get(module,key)
        if type(retval) is dict:
            new_retval = []
            for _k,_v in retval.iteritems():
                new_retval.append(_k)
            retval = new_retval

        if type(retval) is str:
            retval = [retval]

        if type(retval) is list:
            new_retval = []
            for _k in retval:
                if re.search(r"%s" % regex, _k):
                    new_retval.append(_k)
            retval = new_retval

        return retval

    def action(self, module, key, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return retval

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            eval_str_action = "%s['action']" % eval_str

            try:
                exec("retval = %s" % (eval_str_action,))
                return retval
            except:
                return retval

        else:
            is_dict = True
            eval_str  = "conf"

            if multiple_file is True:
                eval_str  += "['%s']['value']" % new_key.pop(0)

            k_len = len(new_key)
            cnt = 0
            for _k in new_key:
                cnt = cnt + 1
                eval_str  += "['%s']" % _k
                if cnt == k_len:
                    break
                eval_str  += "['value']"
                if is_dict is False:
                    eval_str  += "[0]"
                is_dict = not is_dict

            try:
                exec("%s" % (eval_str,))
                eval_str_action = "%s['action']" % eval_str
                exec("retval = %s" % (eval_str_action,))
                return retval
            except:
                return retval


    def iscomment(self, module, key, is_cdp=False, multiple_file=False):
        retval = False

        try:
            self.ConfigArray[module]
        except:
            return retval

        conf = self.ConfigArray[module]

        if type(key) == list:
            pass
        elif type(key) == str:
            key = [key]
        else:
            return retval

        new_key = []
        for _k in key:
            new_key.append(_k.replace("'","\\'"))

        if is_cdp is False:
            eval_str       = "conf['%s']" % "']['value']['".join(new_key)
            eval_str_comment = "%s['comment']" % eval_str

            try:
                exec("retval = %s" % (eval_str_comment,))
                return retval
            except:
                return retval

        else:
            is_dict = True
            eval_str  = "conf"

            if multiple_file is True:
                eval_str  += "['%s']['value']" % new_key.pop(0)

            k_len = len(new_key)
            cnt = 0
            for _k in new_key:
                cnt = cnt + 1
                eval_str  += "['%s']" % _k
                if cnt == k_len:
                    break
                eval_str  += "['value']"
                if is_dict is False:
                    eval_str  += "[0]"
                is_dict = not is_dict

            try:
                exec("%s" % (eval_str,))
                eval_str_comment = "%s['comment']" % eval_str
                exec("retval = %s" % (eval_str_comment,))
                return retval
            except:
                return retval


    def isset(self, module, key, is_cdp=False, multiple_file=False):
        retval = False

        if is_cdp is False:
            if self.get(module,key) is not False:
                retval = True
        else:
            if self.get(module, key, is_cdp=True, multiple_file=multiple_file) is not False:
                retval = True

        return retval

    def order(self, module, key, is_parent_parser=False):
        retval = False

        search_key = []
        if type(key) == list:
            if is_parent_parser is True:
                _sk = key.pop(0)
                search_key.append(_sk)
        elif type(key) == str:
            key = [key]

        search_key.append(self.orders_key)

        try:
            orders = self.get(module, search_key)
            if key in orders:
                return orders.index(key)
        except:
            pass

        return retval

    def insert_order(self, module, key, num=None, is_parent_parser=False):
        retval = False

        search_key = []
        if type(key) == list:
            if is_parent_parser is True:
                _sk = key.pop(0)
                search_key.append(_sk)
        elif type(key) == str:
            key = [key]

        search_key.append(self.orders_key)

        try:
            orders = self.get(module, search_key)
            if key in orders:
                return orders.index(key)
            else:
                if num is None:
                    num = len(orders)
                orders.insert(num,key)
                self.set(module, search_key, orders)
                retval = num
        except:
            self.set(module, search_key, [key])
            retval = 0
            pass

        return retval

    def change_order(self, module, key, num=None, is_parent_parser=False):
        self.delete_order(module, key, is_parent_parser=is_parent_parser)
        return self.insert_order(module, key, num, is_parent_parser=is_parent_parser)

    def append_order(self, module, key, is_parent_parser=False):
        return self.insert_order(module, key, num=None, is_parent_parser=is_parent_parser)

    def delete_order(self, module, key, is_parent_parser=False):
        retval = False

        search_key = []
        if type(key) == list:
            if is_parent_parser is True:
                _sk = key.pop(0)
                search_key.append(_sk)
        elif type(key) == str:
            key = [key]

        search_key.append(self.orders_key)

        try:
            orders = self.get(module, search_key)
            if key in orders:
                num = orders.index(key)
                orders.pop(num)
                self.set(module, search_key, orders)
                retval = num
        except:
            pass

        return retval

    def cdp_isset(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.isset(module,key,is_cdp=True,multiple_file=multiple_file)

        return retval

    def cdp_get(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            return ret[0]
        else:
            return ret

    def cdp_get_comment(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            return ret[1]
        else:
            return retval

    def cdp_get_pre_comment(self, module, key, force=False, multiple_file=False):
        retval = False

        ret = self.cdp_get_comment(module, key, force, multiple_file)
        if type(ret) == list:
            return ret[0]
        else:
            return retval

    def cdp_get_post_comment(self, module, key, force=False, multiple_file=False):
        retval = False

        ret = self.cdp_get_comment(module, key, force, multiple_file)
        if type(ret) == list:
            return ret[1]
        else:
            return retval

    """
    is_opt_multi: if parameter is multidefine-able, is_opt_multi should be True
    """
    def cdp_set(self, module, key, value, force=False, multiple_file=False, is_opt_multi=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            ret[0] = value
        else:
            if is_opt_multi is True:
                ret = value
            else:
                ret = [value,[[],None]]

        return self.set(module, key, ret, is_cdp=True, multiple_file=multiple_file)

    """
    is_opt_multi: if parameter is multidefine-able, is_opt_multi should be True
    """
    def cdp_add(self, module, key, value, force=False, multiple_file=False, is_opt_multi=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            ret[0] = value
        else:
            if is_opt_multi is True:
                ret = value
            else:
                ret = [value,[[],None]]

        return self.add(module, key, ret, is_cdp=True, multiple_file=multiple_file)

    def cdp_set_pre_comment(self, module, key, value, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        if type(value) == list:
            pass
        elif type(value) == str:
            value = [value]
        else:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            ret[1][0] = value
        elif type(ret) == str:
            return retval
            # not implemented.
            ret = [ret,[value,None]]
        else:
            return retval

        return self.set(module, key, ret, is_cdp=True, multiple_file=multiple_file)

    def cdp_set_post_comment(self, module, key, value, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        if type(value) == list:
            value = " ".join(value)
        elif type(value) == str:
            pass
        else:
            return retval

        ret = self.get(module, key, is_cdp=True, multiple_file=multiple_file)
        if type(ret) == list:
            ret[1][1] = value
        elif type(ret) == str:
            return retval
            # not implemented.
            ret = [ret,[[],value]]
        else:
            return retval

        return self.set(module, key, ret, is_cdp=True, multiple_file=multiple_file)

    def cdp_unset(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        return self.unset(module, key, is_cdp=True, multiple_file=multiple_file)

 
    def cdp_action(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.action(module, key, is_cdp=True, multiple_file=multiple_file)
        return retval


    def cdp_delete(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.delete(module, key, is_cdp=True, multiple_file=multiple_file)
        return retval


    def cdp_iscomment(self, module, key, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.iscomment(module, key, is_cdp=True, multiple_file=multiple_file)
        return retval


    def cdp_comment(self, module, key, recursive=False, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.comment(module, key, recursive=recursive, is_cdp=True, multiple_file=multiple_file)
        return retval


    def cdp_uncomment(self, module, key, recursive=False, force=False, multiple_file=False):
        retval = False

        isCommentDeal = False
        try:
            base_parser_name = self.ConfigArray[module]['@BASE_PARSER']['value']
            if base_parser_name == "commentDealParser" or base_parser_name == "xmlLikeConfParser":
                isCommentDeal = True
        except:
            pass

        if isCommentDeal is False and force is False:
            return retval

        retval = self.uncomment(module, key, recursive=recursive, is_cdp=True, multiple_file=multiple_file)
        return retval


"""
aop = DictOp()
aop.addconf("foo",{})
aop.set("foo",["h'oge1","hoge2","hoge3-0"],"fuga1")
aop.set("foo",["h'oge1","hoge2","hoge3-1"],"fuga2")
aop.add("foo",["h'oge1","hoge2","hoge3-2"],"fuga2")
aop.delete("foo",["h'oge1","hoge2","hoge3-2"])
aop.uncomment("foo",["h'oge1","hoge2","hoge3-2"])
aop.comment("foo",["h'oge1","hoge2","hoge3-2"])
aop.preprint_r("foo")
aop.preprint_r("foo",["h'oge1"])
print aop.query("foo",["h'oge1","hoge2"],"^oge3-[01]")
print aop.action("foo",["h'oge1","hoge2","hoge3-2"])
print aop.iscomment("foo",["h'oge1","hoge2","hoge3-2"])
print aop.isset("foo",["h'oge1","hoge2","hoge3-2"])
print aop.isset("foo",["h'oge1","hoge2","hoge3-5"])
print aop.isset("foo",["h'oge1","hoge3","hoge3-2"])
print aop.isset("foo",["h'oge1","hoge2"])
print aop.getconf("foo")
print aop.getconf("bar")
"""
