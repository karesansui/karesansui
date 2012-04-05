#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import re

from karesansui.lib.utils import *

class TestUtils(unittest.TestCase):

    def setUp(self):
      return True

    def tearDown(self):
      return True

    def test_dummy(self):
        self.assertEqual(True,True)
 
    def test_dotsplit(self):
        ret = dotsplit("foo.bar.gah,goh")
        self.assertEqual(ret,("foo.bar", "gah,goh"))
 
    def test_toplist(self):
        ret = toplist("foo")
        self.assertEqual(ret,["foo",])
 
    def test_comma_split(self):
        ret = comma_split("1a,2b,3c,4d")
        self.assertEqual(ret,["1a","2b","3c","4d"])
 
    def test_uniq_sort(self):
        ret = uniq_sort(["z1","z0","a1","19","21","20","19"])
        self.assertEqual(ret,["19","20","21","a1","z0","z1"])
 
    def test_dec2hex(self):
        self.assertEqual(dec2hex(10),"A")
 
    def test_dec2oct(self):
        self.assertEqual(dec2oct(10),"12")
 
    def test_hex2dec(self):
        self.assertEqual(hex2dec("A"),10)
 
    def test_oct2dec(self):
        self.assertEqual(oct2dec("12"),10)

    def test_next_number(self):
        ret = next_number(10,20,[10,11,12,13])
        self.assertEqual(ret,14)

    def test_generate_uuid(self):
        uuid = string_from_uuid(generate_uuid())
        self.assertEqual(is_uuid(uuid),True)

    def test_generate_uuid_reverse(self):
        old_uuid = generate_uuid()
        uuid_str = string_from_uuid(old_uuid)
        new_uuid = string_to_uuid(uuid_str)
        self.assertEqual(old_uuid,new_uuid)

    def test_generate_mac_address(self):
        addr = generate_mac_address()
        regex = '^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'
        m = re.compile(regex).search(addr)
        self.assertNotEqual(m,None)

    def test_execute_command_success(self):
        ret,res = execute_command(["ls","-l"])
        self.assertEqual(ret,0)

    def test_execute_command_failure(self):
        ret,res = execute_command(["invalid_command","-l"])
        self.assertNotEqual(ret,0)

class SuiteUtils(unittest.TestSuite):
    def __init__(self):
        tests = ['test_dummy',
                 'test_dotsplit',
                 'test_toplist',
                 'test_comma_split',
                 'test_uniq_sort',
                 'test_dec2hex',
                 'test_dec2oct',
                 'test_hex2dec',
                 'test_oct2dec',
                 'test_next_number',
                 'test_generate_uuid',
                 'test_generate_uuid_reverse',
                 'test_generate_mac_address',
                 'test_execute_command_success',
                 'test_execute_command_failure',
                 ]
        unittest.TestSuite.__init__(self,map(TestUtils, tests))

def all_suite_utils():
    return unittest.TestSuite([SuiteUtils()])

def main():
    unittest.TextTestRunner(verbosity=2).run(all_suite_utils())
    
if __name__ == '__main__':
    main()
