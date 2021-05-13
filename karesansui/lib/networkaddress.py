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

import re

class NetworkAddress:
    """
    <comment-ja>
    ネットワークアドレスやIPアドレスなどの文字列を操作するクラス
    </comment-ja>
    <comment-en>
    A class to manipulate strings of network address, ip address, etc...
    </comment-en>
    """

    def __init__(self, addr=None):
        """
        <comment-ja>
        "192.168.0.1/24", "192.168.0.1/255.255.255.0"等の種々のIPアドレス指定文字列を操作するクラスのコンストラクタ

        
        @param self: -
        @param addr: アドレス文字列
        @return: なし
        </comment-ja>
        <comment-en>
        constructor of class for manipulating the strings of
        various address formats like "192.168.0.1/24", "192.168.0.1/255.255.255.0".           
        @param self: The object pointer
        @param addr: The string of network address or ip address
        @return: none
        </comment-en>
        """
        self.ip_format = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        self.ipaddr    = None
        self.network   = None
        self.netmask   = None
        self.netlen    = None
        self.cidr      = None
        self.broadcast = None
        if addr != None:
          self.set_network(addr)

    def __repr__(self):
        return '%s/%s' % (self.ipaddr, self.netmask)

    def valid_addr(self, addr=None):
        """
        <comment-ja>
        アドレス形式をチェックする

        @param self: -
        @param addr: アドレス文字列
        @return: アドレス形式が正しければTrue、不正ならFalse
        </comment-ja>
        <comment-en>
        Validate the string of address format

        @param self: The object pointer
        @param addr: The string of address format
        @return: If the specified address is valid, it returns True.
                 If invalid, it returns False.
        </comment-en>
        """
        if addr == None:
          addr = self.ipaddr

        try:
            octets = addr.split('.')
            assert len(octets) == 4
            for x in octets:
                assert 0 <= int(x) <= 255
        except:
            return False
        return True

    def valid_netlen(self, length):
        """
        <comment-ja>
        ネットワーク長をチェックする

        @param self: -
        @param length: ネットワーク長
        @return: アドレス形式が正しければTrue、不正ならFalse
         </comment-ja>
        <comment-en>
        @param self: The object pointer
        @param length: network length
        @return: If the specified address is valid, it returns True.
                 If invalid, it returns False.
         </comment-en>
        """
        try:
            assert 0 <= int(length) <= 32
        except:
            return False
        return True

    def valid_netmask(self, addr):
        """
        <comment-ja>
        ネットマスクをチェックする
        @param self: -
        @param addr: ネットマスク文字列
        @return: アドレス形式が正しければTrue、不正ならFalse
        </comment-ja>
        <comment-en>
        @param self: The object pointer
        @param addr: The string that stands for netmask
        @return: If the specified address is valid, it returns True.
                 If invalid, it returns False.
        </comment-en>
        """
        if self.valid_addr(addr):
            octets = addr.split('.')
            mask = 0x00
            cnt = 0
            for x in octets:
                mask = (int(x) << (24 - 8*cnt)) | mask
                cnt = cnt + 1
            flag = True
            for x in range(32):
                bit = mask & (0x01 << 31-x)
                if bit > 0:
                    if flag == False:
                        return False
                    flag = True
                else:
                    flag = False
        else:
            return False
        return True

    def valid_cidr(self, string):
        retval = False

        p = re.compile(r"^(?P<ipaddr>"+self.ip_format+")/(?P<netlen>\d{1,2})$")
        m = p.match(string)
        if m:
            netlen = m.group("netlen")
            retval = self.valid_netlen(int(netlen))

        return retval


    def parse_addr(self, addr):
        """
        <comment-ja>
        "192.168.0.1/24", "192.168.0.1/255.255.255.0"等の種々のアドレス文字列をパースする。ネットマスク部を省略した場合には、32ビット（255.255.255.255）だとみなされる。
    
        @param self: -
        @param addr: アドレス文字列
        @return: アドレスの各形式を格納した連想配列（辞書）
        </comment-ja>
        <comment-en>
        Parse any kind of address format like "192.168.0.1/24", "192.168.0.1/255.255.255.0". If you omit netmask part, it implicits 32bit netmask address(255.255.255.255) .

        @param self: The object pointer
        @param addr: The string of address format
        @return: The hash table that various format of the specified address is stored in.
        </comment-en>
        """
        type = None
        ipaddr = None
        netmask = None
        cidr = None
        netlen = None

        is_cidr = self.valid_cidr(addr)
        if is_cidr is True:
            p = re.compile(r"^(?P<ipaddr>"+self.ip_format+")/(?P<netlen>\d{1,2})$")
            m = p.match(addr)
            if not m:
                return False
            else:
                type  = "cidr"
                ipaddr = m.group("ipaddr")
                netlen = int(m.group("netlen"))
                cidr = addr

        else:
            p = re.compile(r"^(?P<ipaddr>"+self.ip_format+")/(?P<netmask>"+self.ip_format+")$")
            m = p.match(addr)
            if not m:
                p = re.compile(r"^(?P<ipaddr>"+self.ip_format+")$")
                m = p.match(addr)

                if not m:
                    return False
                else:
                    type    = "ip"
                    ipaddr  = m.group("ipaddr")
                    netmask = "255.255.255.255"
                    netlen  = 32

            else:
                type    = "mask"
                ipaddr  = m.group("ipaddr")
                netmask = m.group("netmask")

        if ipaddr:
            if not self.valid_addr(ipaddr):
                return False

        if netlen:
            if not self.valid_netlen(netlen):
                return False

        if netmask:
            if not self.valid_netmask(netmask):
                return False

        return {
                "type":type,
                "ipaddr":ipaddr,
                "netmask":netmask,
                "netlen":netlen,
                "cidr":cidr,
               }

    def netlen_from_netmask(self, netmask):
        """
        <comment-ja>
        ネットマスクからネットワーク長を求める
        
        @param self: -
        @param netmask: ネットマスク文字列
        @return: ネットワーク長
        </comment-ja>
        <comment-en>
        Calculate network length by specified netmask
        
        @param self: The object pointer
        @param netmask: The string that stands for netmask
        @return: The integer of network length
        </comment-en>
        """
        netlen = 0
        octets = netmask.split('.')
        mask = 0x00
        cnt = 0
        for x in octets:
            mask = (int(x) << (24 - 8*cnt)) | mask
            cnt = cnt + 1
        for x in range(32):
            bit = mask & (0x01 << 31-x)
            if bit > 0:
                netlen = netlen + 1
            else:
                break
        return netlen

    def netlen_to_netmask(self, netlen):
        """
        <comment-ja>
        ネットワーク長からネットマスクを求める

        @param self: -
        @param netlen: ネットワーク長
        @return: ネットワークマスク文字列
        </comment-ja>
        <comment-en>
        Calculate netmask by specified network length

        @param self: The object pointer
        @param netlen: The integer of network length
        @return: The string that stands for netmask
        </comment-en>
        """
        netmask_bit = "%08x" %( (0xffffffff >> netlen) ^ 0xffffffff)
        netmask = ''
        for x in range(0,8,2):
            if netmask != '':
                netmask += "."
            netmask += str(int(netmask_bit[x:x+2],16))
        return netmask

    def set_network(self, addr):
        """
        <comment-ja>
        指定したネットワークアドレス文字列を解析し、そのアドレスの各種要素(CIDR、ネットワーク長など)を変数にセットする。
        ネットワークアドレス文字列には、"192.168.0.1/24"、"192.168.0.1/255.255.255.0"等、parse_addrメソッドで有効な文字列を指定する必要がある。
        
        @param self: -
        @param addr: ネットワークアドレス文字列
        @return: なし
        </comment-ja>
        <comment-en>
        Analize specified network address string, then set the various elements of its address each variable. Network address must be a format valid for parse_addr method.
        
        @param self: The object pointer
        @param addr: The string that stands for network address
        @return: none
        </comment-en>
        """
        res = self.parse_addr(addr)

        if res == False:
          return False

        self.ipaddr = res['ipaddr']

        if res['netmask'] == None and res['netlen'] != None:
            self.netmask = self.netlen_to_netmask(res['netlen'])
        else:
            self.netmask = res['netmask']

        if res['netlen'] == None and res['netmask'] != None:
            self.netlen = self.netlen_from_netmask(res['netmask'])
        else:
            self.netlen = res['netlen']

        cnt = 0
        self.network = ''
        for (x,y) in zip(self.ipaddr.split('.'),self.netmask.split('.')):
            if self.network != '':
                self.network += "."
            if cnt == 3:
                self.first_ip = self.network + "%d" % ((int(x) & int(y)) + 1)
            self.network += "%d" % (int(x) & int(y))
            cnt = cnt + 1

        if self.netlen < 32:
            mask = 0x00
            bit = (0xffffffff >> self.netlen)

            octets = self.network.split('.')
            cnt = 0
            for x in octets:
                mask = mask | (int(x) << (24 - 8*cnt))
                cnt = cnt + 1
            broadcast_bit = "%08x" %( mask | bit )
            self.broadcast = ''
            for x in range(0,8,2):
                if self.broadcast != '':
                    self.broadcast += "."
                if x == 6:
                    self.last_ip = self.broadcast + str(int(broadcast_bit[x:x+2],16) - 1)
                self.broadcast += str(int(broadcast_bit[x:x+2],16))


        self.cidr = "%s/%d" % (self.network, self.netlen)

    def network_includes_address(self, addr):
        """
        <comment-ja>
        指定したIPアドレスが同じネットワーク上にあるかどうかを判定する。

        @param self: -
        @param ip: IPアドレス文字列 ('192.168.0.1'等)。ネットマスク部も指定可能だが無視される（判定にはself.netmaskが使用される）。
        @return: boolean
        </comment-ja>
        <comment-en>
        Checks if specified address is on the same network. Netmask part will be ignored (self.network will be used for check).

        @param self: The object pointer
        @param ip: IP address to check
        @return: boolean
        </comment-en>
        """
        na = NetworkAddress(addr)
        na.set_network(na.ipaddr + '/' + self.netmask)
        return na.network  == self.network

    def get(self, type, format=None):
        """
        <comment-ja>
        ネットワークアドレスの指定した要素の値を取得する

        @param self: -
        @param type: ネットワークアドレスの要素（broadcast,cidrなど）
        @param format: 'num'を指定した場合には、ネットワークアドレスを数値で返す（文字列ではなく）
        @return: 指定した要素の値
        </comment-ja>
        <comment-en>
        Get value of the specified network element

        @param self: The object pointer
        @param type: The element of network address
        @param format: if 'num' is specified, return addresses in number (not string).
        @return: Value of specified network element
        </comment-en>
        """
        #var = 'self.' + type
        #return eval(var)
        if format == 'num':
            value = getattr(self, type)
            if self.valid_addr(value):
                return self.addrtonum(value)
            else:
                raise ValueError('"%s" is not in valid address format.' % type)
        else: 
            return getattr(self, type)

    @classmethod    
    def addrtonum(cls, addr):
        num = 0
        fields = addr.split('.')
        for i in range(0, len(fields)):
            num += pow(256, len(fields) - i - 1) * int(fields[i])
        return num

