#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import re

from karesansui.lib.networkaddress import *

class TestNetworkAddress(unittest.TestCase):

    _targets = {'valid_ipaddr0':'1.2.3.4',
                'valid_ipaddr1':'192.168.0.4',
                'invalid_ipaddr0':'1.2.3.256',
                'invalid_ipaddr1':'.2.3.256',
                'valid_cidr0':'1.2.3.0/24',
                'valid_cidr1':'192.168.0.0/16',
                'invalid_cidr0':'1.2.3.0/33',
                'invalid_cidr1':'1.2.3/33',
                'valid_netmask0':'255.255.0.0',
                'valid_netmask1':'255.255.255.128',
                'invalid_netmask0':'255.256.1.1',
                'invalid_netmask1':'255.255.',
                }

    def setUp(self):
      return True

    def tearDown(self):
      return True

    def test_valid_addr(self):
        for target in self._targets.keys():
          p = re.compile("^valid_")
          if p.match(target):
            self._t = NetworkAddress(self._targets[target])
            self.assertEqual(self._t.valid_addr(),True)

    def test_invalid_addr(self):
        for target in self._targets.keys():
          p = re.compile("^invalid_")
          if p.match(target):
            self._t = NetworkAddress(self._targets[target])
            self.assertEqual(self._t.valid_addr(),False)

    def test_valid_netlen(self):
        for i in xrange(0,32):
            self._t = NetworkAddress()
            self.assertEqual(self._t.valid_netlen(i),True)
 
    def test_invalid_netlen(self):
        for i in xrange(33,35):
            self._t = NetworkAddress()
            self.assertEqual(self._t.valid_netlen(i),False)

    def test_valid_netmask(self):
        for target in self._targets.keys():
          p = re.compile("^valid_netmask")
          if p.match(target):
            self._t = NetworkAddress()
            self.assertEqual(self._t.valid_netmask(self._targets[target]),True)
 
    def test_invalid_netmask(self):
        for target in self._targets.keys():
          p = re.compile("^invalid_netmask")
          if p.match(target):
            self._t = NetworkAddress()
            self.assertEqual(self._t.valid_netmask(self._targets[target]),False)
 
class SuiteNetworkAddress(unittest.TestSuite):
    def __init__(self):
        tests = ['test_valid_addr', 'test_invalid_addr',
                 'test_valid_netlen', 'test_invalid_netlen',
                 'test_valid_netmask', 'test_invalid_netmask',
                 ]
        unittest.TestSuite.__init__(self,map(TestNetworkAddress, tests))

def all_suite_networkaddress():
    return unittest.TestSuite([SuiteNetworkAddress()])

def main():
    unittest.TextTestRunner(verbosity=2).run(all_suite_networkaddress())
    
if __name__ == '__main__':
    main()
