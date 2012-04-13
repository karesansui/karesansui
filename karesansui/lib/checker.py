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

"""<description>
<comment-ja>
HTMLフォームのバリデーションクラスを定義する
</comment-ja>
<comment-en>
Define the class for HTML Form Validation
</comment-en>

@file:   checker.py
@author: Taizo ITO <taizo@karesansui-project.info>
@copyright:    
"""

import sys
import re
import os
import os.path
import gettext
import imghdr
import karesansui
from karesansui.lib.const import DEFAULT_LANGS, IMAGE_EXT_LIST, MACHINE_HYPERVISOR
from karesansui.lib.const import XEN_KEYMAP_DIR, KVM_KEYMAP_DIR

from karesansui.lib.utils import str2datetime, is_int, is_ascii, is_uuid, \
     get_ifconfig_info
from karesansui.lib.networkaddress import NetworkAddress
from karesansui.db.model._2pysilhouette import JOBGROUP_STATUS
from karesansui.lib.virt.virt import KaresansuiVirtConnection
from karesansui.lib.firewall.iptables import KaresansuiIpTables

CHECK_EMPTY     = 1<<0   #フォームが空でないか
CHECK_VALID     = 1<<1   # 値が正当か
CHECK_NOTROOT   = 1<<2   # "/"でないか(ルートディレクトリではまずい場合)
CHECK_STARTROOT = 1<<3   # "/"で始まっているか(絶対パスでないとまずい場合)
CHECK_MIN       = 1<<4   # 数値の最小値(UID,GID,Portなど)
CHECK_MAX       = 1<<5   # 数値の最大値(UID,GID,Portなど)
ALLOW_REGEX     = 1<<6   # 正規表現を許す(ディレクトリなど)
CHECK_LENGTH    = 1<<7   # whether the length of string is long enough
CHECK_ONLYINT   = 1<<8   # whether value consists of the integer only
CHECK_ONLYSPACE = 1<<9   # whether value consists of the space char only
CHECK_EXIST     = 1<<10  # 存在するか(ファイルなど)
CHECK_MAKEDIR   = 1<<11  # 存在しないディレクトリを自動生成
CHECK_ISDIR     = 1<<12  # ディレクトリかどうか
CHECK_LENGTH    = 1<<13  # 長さが十分かどうか(パスワード)
WARN_LENGTH     = 1<<14  # 長さが十分かどうか(パスワード)常にtrueを返す
CHECK_CHAR      = 1<<15  # 数字だけではないか
CHECK_DICTVALUE = 1<<16  # 辞書の値と一致するかどうか
CHECK_DICTKEY   = 1<<17  # 辞書のキーと一致するかどうか
CHECK_UNIQUE    = 1<<18  # 一意であるか

t = gettext.translation('messages', karesansui.dirname + "/locale")
_ = t.ugettext
#_ = t.gettext

class Checker(object):
    """<comment-ja>
    HTMLフォームの入力チェッククラス
    </comment-ja>
    <comment-en>
    The class to validate input value of HTML form
    </comment-en>
    """

    def __init__(self):
        self.errors = []

    def add_error(self, msg):
        self.errors.append(unicode(msg))

    def check_empty(self, name, value):
        """<comment-ja>
        値が空文字列でないかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする文字列
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether a specified string is empty

        @param name: Item name
        @param value: string
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if value.strip() == "":
            ret_val = False
            self.add_error(_('%s is missing.') % (name,))

        return ret_val

    def check_length(self, name, value, min=None, max=None):
        """<comment-ja>
        文字列の長さが指定範囲内であるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする文字列
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether the length of string is in specified range.

        @param name: Item name
        @param value: string
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if max != None and len(value) > max:
            ret_val = False
            self.add_error(_('%s must be shorter than %d characters.') % (name, max))
        if min != None and len(value) < min:
            ret_val = False
            self.add_error(_('%s must be longer than %d characters.') % (name, min))

        return ret_val

    def check_string(self, name, value, check, regex, min=None, max=None):
        """<comment-ja>
        文字列が指定したフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする文字列
        @param check: チェックする条件
        @param regex: 不正文字列を示す
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether specified string is valid format.

        @param name: Item name
        @param value: string
        @param check: condition to determine
        @param regex: regular expression that stands for invalid strings
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
      
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if (check & CHECK_VALID) and regex:
            regex_str = "(?P<match>%s)" % regex
            m = re.compile(regex_str).search(value)
            if m:
                ret_val = False
                self.add_error(_('%s includes invalid character[s] %s.') % (name, m.group("match")))

        if check & CHECK_ONLYSPACE:
            regex_str = "\s+"
            if re.compile(r"""^\s+$""").search(value):
                ret_val = False
                self.add_error(_('%s must not consist of only blank characters.') % (name,))

        return ret_val

    def check_number(self, name, value, check, min=None, max=None):
        """<comment-ja>
        指定した整数値が正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする整数値
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether number is valid format or in specified range.

        @param name: Item name
        @param value: interger
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if value!="" and ret_val:
            if check & CHECK_VALID:
                if not re.compile("^[-+]?[0-9]+$").match(value):
                  ret_val = False
                  self.add_error(_('%s is not numerical value.') % (name,))

            if ret_val and (check & CHECK_MIN):
                value = int(value)
                if value < min:
                    ret_val = False
                    self.add_error(_('%s must be greater than %d.') % (name, min))
 
            if ret_val and (check & CHECK_MAX):
                value = int(value)
                if value > max:
                    ret_val = False
                    self.add_error(_('%s must be smaller than %d.') % (name, max))

        return ret_val

    def check_directory(self, name, value, check):
        """<comment-ja>
        指定したディレクトリが正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするディレクトリパス
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether directory is valid format or exists.

        @param name: Item name
        @param value: path of directory
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ( not(check & CHECK_EMPTY) and value) or ret_val:
            if check & CHECK_VALID:
                if check & ALLOW_REGEX:
                    args = ']*{}[?'
                else:
                    args = ""

                ret_val = self.check_string(name, value, check,
                                    "[^%s+\._\(\)\'&@a-zA-Z0-9\/-]" % args)
                if ret_val is False:
                    self.add_error(_('Available characters are'))
                    self.add_error(_('0-9 a-z A-Z @ & ( ) + - . _ %s') % (args,))
 
            if check & CHECK_ISDIR:
                if os.path.exists(value) and not os.path.isdir(value):
                    ret_val = False
                    self.add_error(_('%s is not a directory.') % (value,))

            if check & CHECK_STARTROOT:
                if not re.compile("^[\"\']?/").match(value):
                    ret_val = False
                    self.add_error(_('%s must start with /.') % (name,))

            if check & CHECK_NOTROOT:
                if re.compile(r"^[\"\' \t]*/[\"\' \t]*$", re.VERBOSE).match(value):
                    ret_val = False
                    self.add_error(_('%s must not be root directory.') % (name,))

            if check & CHECK_EXIST:
                if not os.path.exists(value):
                    ret_val = False
                    self.add_error(_('No such %s [%s].') % (name, value))

        return ret_val

    def check_username(self, name, value, check, min=None, max=None):
        """<comment-ja>
        指定したユーザー名が正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするユーザー名
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether username is valid format.

        @param name: Item name
        @param value: user name
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if value and ret_val:
            if check & CHECK_VALID:

                m1 = re.compile(r'^[a-z]').search(value)
                m2 = re.compile(r'^[a-z][-_\.0-9a-z]*$').search(value)
                if not m1:
                    ret_val = False
                    self.add_error(_('%s must begin with alphabet.') % (name,))
                elif not m2:
                    ret_val = self.check_string(name, value, check,
                                    "[^-_.0-9a-z]", min, max)
                    ret_val = False
                    self.add_error(_('Available characters are'))
                    self.add_error(_('0-9 a-z - . _'))

        if check & CHECK_ONLYSPACE:
            regex_str = "\s+"
            if re.compile(r"""^\s+$""").search(value):
                ret_val = False
                self.add_error(_('%s must not consist of only blank characters.') % (name,))

        return ret_val

    def check_username_with_num(self, name, value, check, min=None, max=None):
        """<comment-ja>
        指定したユーザー名が正しいフォーマットであるかどうかをチェックする
        （ユーザー名の先頭は数値でも可）

        @param name: 入力項目名
        @param value: チェックするユーザー名
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether username is valid format.
        (username can begin with NUMBER)

        @param name: Item name
        @param value: user name
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if ( not(check & CHECK_EMPTY) and value) or ret_val:
            if check & CHECK_VALID:

                m1 = re.compile(r'^[a-zA-Z0-9]').search(value)
                m2 = re.compile(r'^[a-zA-Z0-9][-_\.0-9a-z]*$').search(value)
                if not m1:
                    ret_val = False
                    self.add_error(_('%s must begin with alphabet or number.') % (name,))
                elif not m2:
                    ret_val = False
                    self.add_error(_('%s is in invalid format.') % (name,))
                    self.add_error(_('Available characters are'))
                    self.add_error(_('0-9 a-z - . _'))

        return ret_val

    def check_domainname(self, name, value, check, min=None, max=None, extra_args=None):
        """<comment-ja>
        指定したドメイン名が正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするドメイン名
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether domainname is valid format.

        @param name: Item name
        @param value: domain name
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if extra_args:
            domain = extra_args
        else:
            domain = "your.domain.name"

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if value and ret_val:
            if check & CHECK_VALID:
                if value != "localhost" and not re.compile(r'.*\.').match(value):

                    ret_val = False
                    self.add_error(_('%s must include at least one dot . character.') % (name,))

                if re.compile(r'(^\.|.*\.$|.*\.\.|.*-\.|.*\.-|^-|.*-$)', re.VERBOSE).match(value):
                    ret_val = False
                    self.add_error(_('%s must be specified like %s.') % (name, domain))

                ret_val = self.check_string(name, value, check, "[^-a-zA-Z0-9\.]+") and ret_val
                if ret_val is False:
                    self.add_error(_('Available characters are'))
                    self.add_error(_('a-z A-Z 0-9 . -'))

        return ret_val 

    def check_hostname(self, name, value, check, min=None ,max=None):
        """<comment-ja>
        指定したホスト名が正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするホスト名
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether hostname is valid format. (not FQDN)

        @param name: Item name
        @param value: host name
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if value and ret_val:
            if check & CHECK_VALID:

                if re.compile(r".*\.", re.VERBOSE).match(value):
                    ret_val = False
                    self.add_error(_('%s must not include dot . character.') % (name,))

                if re.compile(r"(^-|.*-$)", re.VERBOSE).match(value):
                    ret_val = False
                    self.add_error(_('%s cannot begin or end with a hyphen.') % (name,))

                ret_val = self.check_string(name, value, check, "[^-a-zA-Z0-9]")
                if ret_val is False:
                    self.add_error(_('Available characters are'))
                    self.add_error(_('a-z A-Z 0-9 -'))

        return ret_val 

    def check_mailaddress(self, name, value, check, min=None, max=None, extra_args=None):
        """<comment-ja>
        指定したメールアドレスが正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするメールアドレス
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether mail address is valid format.

        @param name: Item name
        @param value: mail address
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if extra_args:
            domain = extra_args
        else:
            domain = "your.domain.name"

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if value and ret_val:
            if check & CHECK_VALID:

                regex = "^(?P<localpart>[^@]+)@(?P<domainpart>.+)?$"
                m = re.compile(regex).search(value)
                if m:
                  tstr1 = m.group("localpart")
                  tstr2 = m.group("domainpart")
                  ret_val = ret_val and self.check_username_with_num(name, tstr1, check, 1, 64)
                  ret_val = ret_val and self.check_domainname(_('Domain name part of %s') % (name,), tstr2, CHECK_EMPTY|check, 4, 255, domain)
                else:
                  ret_val = False
                  self.add_error(_('%s is in an invalid format.') % (name,))
                  self.add_error(_('Please specify like username@%s.') % (domain,))

        return ret_val

    def check_ipaddr(self, name, value, check):
        """<comment-ja>
        指定したIPアドレスが正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするIPアドレス
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether IP address is valid format.

        @param name: Item name
        @param value: IP address
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if value and ret_val:
            if check & CHECK_VALID:
                from karesansui.lib.networkaddress import NetworkAddress

                if not NetworkAddress(value).valid_addr():
                    ret_val = False
                    self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_macaddr(self, name, value, check):
        """<comment-ja>
        指定したMACアドレスが正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするMACアドレス
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether MAC address is valid format.

        @param name: Item name
        @param value: MAC address
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and (check & CHECK_VALID) and len(value) > 0:
            regex = '^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'
            m = re.compile(regex).search(value)
            if not m:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_netmask(self, name, value, check):
        """<comment-ja>
        指定したネットマスクが正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするネットマスク
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether netmask is valid format.

        @param name: Item name
        @param value: netmask
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if value and ret_val:
            if check & CHECK_VALID:
                from karesansui.lib.networkaddress import NetworkAddress

                if not NetworkAddress().valid_netmask(value):
                    ret_val = False
                    self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_cidr(self, name, value, check):
        """<comment-ja>
        指定したネットワークアドレス（CIDR）が正しいフォーマットであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするネットワークアドレス
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether cidr-style network address is valid format.

        @param name: Item name
        @param value: network address
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if value and ret_val:
            if check & CHECK_VALID:
                from karesansui.lib.networkaddress import NetworkAddress

                if not NetworkAddress(value).valid_addr():
                    ret_val = False
                    self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_netdev_name(self, name, value, check):
        """<comment-ja>
        指定したネットワークデバイス名が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするネットワークデバイス名
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether network device name is in valid format.

        @param name: Item name
        @param value: Network device name
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and (check & CHECK_VALID):
            regex = "^[a-z][a-z0-9\.\:]{1,12}$" # what is a valid net dev name in linux?
            m = re.compile(regex).search(value)
            if not m:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_network_name(self, name, value, check):
        """<comment-ja>
        指定したネットワーク名が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするネットワーク名
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether network name is in valid format.

        @param name: Item name
        @param value: Network name
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and (check & CHECK_VALID):
            # Depend on maximum length of pid file name for dnsmasq.
            # len("<network_name>.pid") <= 256
            # libvirt allow space or other special chars,
            # but virsh command cannot parse space-included name.
            regex = "^[a-zA-Z0-9][a-zA-Z0-9\_\.\:\-]{0,251}$"
            m = re.compile(regex).search(value)
            if not m:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_password(self, name, pass1, pass2, check, min=None, max=None):
        """<comment-ja>
        指定したパスワードが正しいかどうかをチェックする

        @param name: 入力項目名
        @param pass1: チェックするパスワード
        @param pass2: チェックするパスワード（再入力）
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether two passwords is valid format or same.

        @param name: Item name
        @param pass1: password
        @param pass2: password (retype)
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(pass1, int):
            pass1 = str(pass1)

        if isinstance(pass2, int):
            pass2 = str(pass2)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, pass1)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, pass1, min, max)

        if pass1 != "" or pass2 != "":
            if ret_val and (check & CHECK_VALID):
                if pass1 != pass2:
                    ret_val = False
                    self.add_error(_('%s is mismatched.') % (name,))
                if not is_ascii(pass1):
                    ret_val = False
                    self.add_error(_('%s includes invalid character[s].') % (name))

            if ret_val and (check & WARN_LENGTH):
                if len(pass1) < min or len(pass2) < min:
                    ret_val = False
                    self.add_error(_('WARNING: %s is too short.') % (name,))

            if ret_val and (check & CHECK_CHAR):
                m = re.compile(r'^[0-9]+$').search(pass1)
                if m:
                    ret_val = False
                    self.add_error(_('%s must not consist of only numbers.') % (name,))

        return ret_val

    def check_unique_key(self, name, value, check):
        ret_val = True

        if is_int(value):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
        if ret_val:
            if check & CHECK_VALID: 
                if not is_uuid(value):
                    ret_val = False
                    self.add_error(_('%s is invalid format.') % (name,))
        return ret_val

    def check_datetime_string(self, name, value, check, languages):
        """<comment-ja>
        指定した日付を示す文字列が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: 日時を示す文字列
        @param check: チェックする条件
        @param languages: 言語
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether datetime string is valid format.

        @param name: Item name
        @param value: string of datetime
        @param check: condition to determine
        @param languages: languages
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if is_int(value):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if check & CHECK_VALID:
            try:
                str2datetime(value, DEFAULT_LANGS[languages]['DATE_FORMAT'][0])
             
            except (TypeError, ValueError):
                ret_val = False
                self.add_error(_('%s is invalid format.') % (name,))

        return ret_val

    def check_dictionary(self, name, value, check, extra_args):
        """<comment-ja>
        指定した辞書が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする辞書
        @param check: チェックする条件
        @param extra_args: 調査するキー、値を要素とする配列
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether specified dictionary is valid.

        @param name: Item name
        @param value: dictionary
        @param check: condition to determine
        @param extra_args: array includes the searched value.
        @return: result
        @rtype: boolean
        </comment-en>
        """
        # ret_val is False. Because, suppose that the dictionary does not have the value
        ret_val = False
        empty_val = True

        if is_int(value):
            value = str(value)

        if check & CHECK_EMPTY:
            empty_val = self.check_empty(name, value)
        ret_val = ret_val and empty_val

        if empty_val is True:
            if check & CHECK_DICTVALUE:
                if value in str(extra_args.values()):
                    ret_val = True
                if not ret_val:
                    self.add_error(_('%s is in invalid format.') % (name,))

            if check & CHECK_DICTKEY:
                if extra_args.has_key(value):
                    ret_val = True
                if not ret_val:
                    self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_uri(self, name, value, check):
        """<comment-ja>
        指定したURIが正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするURI
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether uri is valid format.

        @param name: Item name
        @param value: uri
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and (check & CHECK_VALID):
            regex = '^(http|ftp):\/\/[\w.]+\/(\S*)'
            m = re.compile(regex).search(value)
            if not m:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val
          
    def check_languages(self, name, value, check, min=None, max=None):
        """<comment-ja>
        指定した言語が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする言語名
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine language name is valid.

        @param name: Item name
        @param value: language name
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)

        if value.strip() != "":
            if ret_val and (check & CHECK_VALID):
                if not value in DEFAULT_LANGS.keys():
                    ret_val = False
                    self.add_error(_('%s is mismatched.') % (name,))

        return ret_val

    def check_image(self, name, value, check, min=None, max=None):
        """<comment-ja>
        画像データが正しいかどうかをチェックする。

        @param name: 入力項目名
        @param value: チェックする画像データ
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether image data is valid.

        @param name: Item name
        @param value: image data
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        """
        # TODO Image size check
        if ret_val and check & CHECK_LENGTH:
            ret_val = self.check_length(name, value, min, max)
        """

        if ret_val and (check & CHECK_VALID):
                if not value == "":
                    if not imghdr.what(None, value) in IMAGE_EXT_LIST:
                        ret_val = False
                        self.add_error(_('%s is in invalid format.') % (name,))

        return ret_val

    def check_hypervisor(self, name, value, check, min=None, max=None):
        """<comment-ja>
        指定したハイパーバイザーの値が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするハイパーバイザーの値
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine hypervisor name is valid.

        @param name: Item name
        @param value: hypervisor value
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and (check & CHECK_MIN):
            ret_val = self.check_number(name, value, CHECK_MIN, min, max)

        if ret_val and (check & CHECK_MAX):
            ret_val = self.check_number(name, value, CHECK_MAX, min, max)

        if ret_val and (check & CHECK_VALID):
            value = int(value)
            if not value in MACHINE_HYPERVISOR.values():
                ret_val = False
                self.add_error(_('%s is mismatch.') % (name,))

        return ret_val

 
    def check_status(self, name, value, check, status_list = []):
        """<comment-ja>
        状態値が正しい値かチェックする

        @param name: 入力項目名
        @param value: チェックするステータスの値
        @param check: チェックする条件
        @param status_list: 突き合わせるステータスのリスト
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether status data is valid.

        @param name: Item name
        @param value: status value
        @param check: condition to determine
        @param status_list: status value list
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = False
        empty_val = True

        if isinstance(value, int):
            value = str(value)
        if check & CHECK_EMPTY:
            empty_val = self.check_empty(name , value)

        if (empty_val is True) and (check & CHECK_VALID):
            for elem in status_list:
                if value == str(elem): 
                    ret_val = True

            if ret_val is False:
                self.add_error(_('%s is invalid format.') % (name,))

        ret_val = ret_val and empty_val
        return ret_val

    def check_startfile(self, name, value, check):
        """<comment-ja>
        指定した起動ファイル(vmlinuz, initrd)のパスが正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする起動ファイル(vmlinuz, initrd)のパス
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether start file(vmlinuz, initrd) path is valid format.

        @param name: Item name
        @param value: start file(vmlinuz, initrd) path
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ( not(check & CHECK_EMPTY) and value) or ret_val:

            _http_flag = False
            _file_flag = False
            if check & CHECK_VALID:

                regex = '^(http|ftp):\/\/[\w.\-]+\/(\S*)'
                m = re.compile(regex).search(value)
                if m:
                    _http_flag = True

                if re.compile("^[\"\']?/").match(value):
                    _file_flag = True

                if _http_flag is False and _file_flag is False:
                    ret_val = False
                    self.add_error(_('%s is in invalid format.') % (name,))

            if ret_val and (check & CHECK_EXIST):
                # TODO http path exist valid
                if _file_flag is True:
                    if not os.path.exists(value):
                        ret_val = False
                        self.add_error(_('No such %s [%s].') % (name, value))

            return ret_val

    def check_uniqueness(self, names, values, check):
        """<comment-ja>
        与えられた値が一意であるかを確認する。

        @param names: 入力項目名の配列
        @param value: 値の配列
        @param check: チェックする条件(CHECK_UNIQUEのみサポート)
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether values are unique.

        @param names: List of item names.
        @param value: List of values.
        @param check: Condition to check. (supports only CHECK_UNIQUE)
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True
        if len(values) != len(set(values)):
            ret_val = False
            self.add_error(_('Values for %s should be unique.') % (','.join(names),))

        return ret_val

    def check_if_ips_are_in_network(self, names, ips, network, check):
        """<comment-ja>
        与えられたIPアドレス値がネットワークに含まれるかどうかを確認する。
        CHECK_UNIQUEを与えることで、ipsとnetworkを通して各値が一意であるかどうかも確認することができる。

        @param names: 入力項目名の配列
        @param ips: IPアドレス値の配列（'192.168.0.1','192.168.0.1/24'表記。ネットマスクは無視される。）
        @param network: ネットワークアドレスを計算するための文字列（'192.168.0.1/24', '192.168.0.1/255.255.255.0'等）
        @param check: チェックする条件(CHECK_VALID, CHECK_UNIQUEをサポート)
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether IP address are in Network.
        Also checks uniqueness between ips and network when CHECK_UNIQUE provided.

        @param names: List of item names.
        @param ips: List of IP address (strings as '192.168.0.1' or '192.168.0.1/24'. Netmask part will be ignored)
        @param network: String to calculate network address ('192.168.0.1/24', '192.168.0.1/255.255.255.0')
        @param check: Condition to check. (supports CHECK_VALID, CHECK_UNIQUE)
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True
        na = NetworkAddress(network)
        if check & CHECK_VALID:
            for i in range(0, len(ips)):
                ip = ips[i]; name = names[i]
                if not na.network_includes_address(ip):
                    ret_val = False
                    self.add_error(_('%(ip)s for %(name)s is not in network %(cidr)s') % {'ip':ip, 'name':name, 'cidr':na.cidr})

        if check & CHECK_UNIQUE: 
            if len(ips) != len(set(ips)):
                ret_val = False
                self.add_error( _('IP address for %s should be unique.')  % (','.join(names)))

        return ret_val

    def check_ip_range(self, names, ips, check):
        """<comment-ja>
        与えられたIPアドレス値が正しく範囲を表しているかどうかを確認する。

        @param names: 入力項目名の配列
        @param ips: [開始値, 終了値, 独立値]形式の配列。独立値は範囲に含まれない値を表し、省略可能。　
        @param check: チェックする条件（CHECK_VALIDをサポート）
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether IP address are in valid range.

        @param names: List of item names.
        @param ips: List of IP address as [ start_ip, end_ip, individual_ip ]. individual_ip which can be omitted, stands for an IP address not in the range between start_ip and end_ip.
        @param check: Condition to check. (supports CHECK_VALID)
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if check & CHECK_VALID:
            start_ip = NetworkAddress(ips[0]).get('ipaddr', 'num')
            end_ip   = NetworkAddress(ips[1]).get('ipaddr', 'num')

            if not (end_ip > start_ip):
                ret_val = False
                self.add_error( _('IP address range %s to %s is not valid.') % (ips[0], ips[1]) )

            if len(ips) > 2:
                # Perform individual IP check
                ind_ip = NetworkAddress(ips[2]).get('ipaddr', 'num')
                if not((ind_ip < start_ip) or (end_ip < ind_ip)):
                    ret_val = False
                    self.add_error( _('IP address %s should not be in range %s to %s') % (ips[2], ips[0], ips[1]))

        return ret_val

    def check_virt_network_address_conflict(self, name, cidr, ignore_names, check):
        """<comment-ja>
        与えられたネットワークIPアドレス範囲がlibvirt上の他のネットワークアドレス範囲
        と競合しないかどうか（ネットワークアドレス範囲の重なり合いが無いか）を確認する。

        @param name: 入力項目名
        @param cidr: '192.168.0.1/24', '192.168.0.1/255.255.255.0'形式でのネットワークアドレス指定。
        @param ignore_names: 衝突をチェックしない／無視するネットワーク名の配列。
        @param check: チェックする条件（CHECK_VALIDをサポート）
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether a network IP address range does not conflict with other libvirt network.

        @param names: Item name
        @param cidr: Network address specification in '192.168.0.1/24' or '192.168.0.1/255.255.255.0' format.
        @param ignore_names: List of name of networks to ignore/do not perform check.
        @param check: Condition to check. (supports CHECK_VALID)
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        new_na = NetworkAddress(cidr)

        if check & CHECK_VALID:
            try:
                kvc = KaresansuiVirtConnection()
                networks = kvc.search_kvn_networks()
                for network in networks:
                    if network.get_network_name() in ignore_names:
                        pass
                    else:
                        info = network.get_info()
                        existing_na_cidr = '%s/%s' % (info['ip']['address'], info['ip']['netmask'])
                        existing_na = NetworkAddress(existing_na_cidr)

                        conflict = False
                        # New-one in existing-one
                        if existing_na.network_includes_address(new_na.network): conflict = True
                        # Existing-one in new-one
                        if new_na.network_includes_address(existing_na.network): conflict = True
                        if conflict:
                            ret_val = False
                            self.add_error( _('Network address %s for %s is used by other network (%s)') % (cidr, name, network.get_network_name()))
            finally:
                kvc.close()

        return ret_val

    def check_forward_mode(self, name, value, check):
        """<comment-ja>
        指定した転送モード(networkの)が正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする転送モード
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether network forward mode is in a valid format.

        @param name: Item name
        @param value: Forward mode
        @param check: Condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;
        if check & CHECK_VALID:
            if value == 'nat' or value == '':
                ret_val = True
            else:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name))
        return ret_val

    def check_firewall_policy(self, name, value, check):
        """<comment-ja>
        指定したポリシーが正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするポリシー
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether firewall policy is valid format.

        @param name: Item name
        @param value: firewall policy
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """

        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and (check & CHECK_VALID):
            if not value in KaresansuiIpTables().basic_targets['filter']:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name))

        return ret_val
    
    def check_firewall_protocol(self, name, value, check):
        """<comment-ja>
        指定したプロトコルが正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするプロトコル
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether firewall policy is valid format.

        @param name: Item name
        @param value: firewall protocol
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """

        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)
 
        if ret_val and value and (check & CHECK_VALID):
            if not value in KaresansuiIpTables().chain_protos:
                ret_val = False
                self.add_error(_('%s is in invalid format.') % (name))

        return ret_val

    def check_firewall_if(self, name, value, check): 
        """<comment-ja>
        指定したインターフェースが実在するものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするプロトコル
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether firewall policy is valid format.

        @param name: Item name
        @param value: firewall protocol
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """

        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and value and (check & CHECK_EXIST):
            devtype_regexs = {
                "phy":"^(lo|eth)",
                "vir":"^(xenbr|virbr|vif|veth)",
                }
            devtype_phy_regex = re.compile(r"%s" % devtype_regexs['phy'])
            devtype_vir_regex = re.compile(r"%s" % devtype_regexs['vir'])
            
            devs = {}
            interfaces = []
            devs['phy'] = []
            devs['vir'] = []
            devs['oth'] = []
            cidrs = []
            ips = []
            for dev,dev_info in get_ifconfig_info().iteritems():
                try:
                    if devtype_phy_regex.match(dev):
                        devs['phy'].append(dev)
                    elif devtype_vir_regex.match(dev):
                        devs['vir'].append(dev)
                    else:
                        devs['oth'].append(dev)
                    if dev_info['ipaddr'] is not None:
                        if not dev_info['ipaddr'] in ips:
                            ips.append(dev_info['ipaddr'])
                    if dev_info['cidr'] is not None:
                        if not dev_info['cidr'] in cidrs:
                            cidrs.append(dev_info['cidr'])
                except:
                    pass
            for devlist in devs.itervalues():
                interfaces.extend(devlist)

            if not value in interfaces:
                ret_val = False
                self.add_error(_('No such %s [%s].') % (name, value))

        return ret_val


    def check_keymap(self, name, value, check, domain_type="xen"):
        """<comment-ja>
        指定したキーマップが実在するものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックするキーマップ
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether keymap is valid format.

        @param name: Item name
        @param value: keymap
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if ret_val and value and (check & CHECK_EXIST):
            exec("keymap_dir = %s_KEYMAP_DIR" % domain_type.upper())
            if not os.path.exists(keymap_dir + '/' + value):
                ret_val = False
                self.add_error(_('No such %s [%s].') % (name, value))

        return ret_val

    def check_fraction(self, name, value, check, min=None, max=None, precision=None):
        """<comment-ja>
        指定した実数値が正しいものであるかどうかをチェックする

        @param name: 入力項目名
        @param value: チェックする実数値
        @param check: チェックする条件
        @param min: 最小値
        @param max: 最大値
        @param precision: 小数点以下の桁数
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether fraction is valid format or in specified range.

        @param name: Item name
        @param value: interger
        @param check: condition to determine
        @param min: the minimum length
        @param max: the maximum length
        @param precision: Number of decimal places
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True;

        if isinstance(value, int):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if value!="" and ret_val:
            arr_dp = re.compile("^([-+]?[0-9]+)\.([0-9]+)$").match(value)

            if arr_dp:
                integer = arr_dp.group(1)
                fraction = arr_dp.group(2)
            else:
                integer = value
                fraction = "0"

            if check & CHECK_VALID:
                if not re.compile("^[-+]?[0-9]+$").match(integer) or not re.compile("^[0-9]+$").match(fraction):
                    ret_val = False
                    self.add_error(_('%s is not integer or decimal fraction.') % (name,))
                elif len(fraction) > precision:
                    ret_val = False
                    self.add_error(_('(%s) Length of figures after point must be equal or less than %s.') % (name,str(precision)))

            if ret_val and (check & CHECK_MIN):
                value = float(value)
                if value < min:
                    ret_val = False
                    self.add_error(_('%s must be greater than %d.') % (name, min))

            if ret_val and (check & CHECK_MAX):
                value = float(value)
                if value > max:
                    ret_val = False
                    self.add_error(_('%s must be smaller than %d.') % (name, max))

        return ret_val

    def check_time_string(self, name, value, check):
        """<comment-ja>
        時刻を示す文字列が正しいかどうかをチェックする

        @param name: 入力項目名
        @param value: 時刻を示す文字列
        @param check: チェックする条件
        @return: チェック結果
        @rtype: boolean
        </comment-ja>
        <comment-en>
        Determine whether time string is valid format.

        @param name: Item name
        @param value: string of datetime
        @param check: condition to determine
        @return: result
        @rtype: boolean
        </comment-en>
        """
        ret_val = True

        if is_int(value):
            value = str(value)

        if check & CHECK_EMPTY:
            ret_val = self.check_empty(name, value)

        if check & CHECK_VALID:
            time_regex = re.compile("^([0-1][0-9]|[2][0-3]|[0-9]):[0-5][0-9]$")
            if not time_regex.match(value):
                ret_val = False
                self.add_error(_('%s is invalid format.') % (name,))

        return ret_val
