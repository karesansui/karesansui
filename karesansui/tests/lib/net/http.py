#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import re

from karesansui.lib.net.http import *
import karesansui.lib.net.http
_wget_proxy = karesansui.lib.net.http._wget_proxy

class TestHttp(unittest.TestCase):

    def setUp(self):
      return True

    def tearDown(self):
      return True

    def test__wget_proxy_1(self):
        url="http://ftp.jaist.ac.jp/pub/Linux/CentOS/5.3/os/x86_64/images/xen/initrd.img"
        file="/tmp/karesansui_test__wget_proxy_1"
        proxy_host="foo.example.com"
        proxy_port="80"
        user="hayashi"
        password="hayashi"
        
        _wget_proxy(url,file,proxy_host,proxy_port,user,password)

    def test__wget_proxy_2(self):
        url="http://ftp.jaist.ac.jp/pub/Linux/CentOS/5.3/os/x86_64/images/xen/initrd.img"
        file="/tmp/karesansui_test__wget_proxy_2"
        proxy_host="foo.example.com"
        proxy_port="80"
        user="nopass"
        password=None
        
        _wget_proxy(url,file,proxy_host,proxy_port,user,password)

    def test__wget_proxy_3(self):
        url="http://ftp.jaist.ac.jp/pub/Linux/CentOS/5.3/os/x86_64/images/xen/initrd.img"
        file="/tmp/karesansui_test__wget_proxy_3"
        proxy_host="foo.example.com"
        proxy_port="9080"
        user=None
        password=None
        
        _wget_proxy(url,file,proxy_host,proxy_port,user,password)

    def test__wget_proxy_4(self):
        url="http://ftp.jaist.ac.jp/pub/Linux/CentOS/5.3/os/x86_64/images/xen/initrd.img"
        file="/tmp/karesansui_test__wget_proxy_4"
        proxy_host="foo.example.com"
        proxy_port="9080"
        user=None
        password=None
        
        _wget_proxy(url,file,proxy_host,proxy_port,user,password)

class SuiteHttp(unittest.TestSuite):
    def __init__(self):
        tests = ['test__wget_proxy_1',
                 'test__wget_proxy_2',
                 'test__wget_proxy_3',
                 'test__wget_proxy_4',
                 ]
        unittest.TestSuite.__init__(self,map(TestHttp, tests))

def all_suite_http():
    return unittest.TestSuite([SuiteHttp()])

def main():
    unittest.TextTestRunner(verbosity=2).run(all_suite_http())
    
if __name__ == '__main__':
    main()
