#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import tempfile

from karesansui.lib.file.k2v import *

class TestK2V(unittest.TestCase):

    _w = {'key.1':'h oge',
         'key.2':'fo o',
         'key.3':'bar ',
         'key.4':' piyo',
         'key.5':'s p am'}

    def setUp(self):
        self._tmpfile = tempfile.mkstemp()
        fp = open(self._tmpfile[1], 'w')
        self._t = K2V(self._tmpfile[1])
    
    def tearDown(self):
        os.unlink(self._tmpfile[1])

    def test_write_0(self):
        _d = self._t.write(self._w)
        for i in xrange(1,6):
            self.assertEqual(self._w['key.%d'%i],_d['key.%d'%i])

    def test_read_0(self):
        _d = self._t.read()
        for i in xrange(1,6):
            self.assertEqual(self._w['key.%d'%i],_d['key.%d'%i])
        
    def test_lock_sh_0(self):
        self.fail('TODO:')

    def test_lock_ex_0(self):
        self.fail('TODO:')

    def test_lock_un_0(self):
        self.fail('TODO:')

        
class SuiteK2V(unittest.TestSuite):
    def __init__(self):
        tests = ['test_write_0', 'test_read_0',
                 'test_lock_ex_0', 'test_lock_un_0']
        unittest.TestSuite.__init__(self,map(TestK2V, tests))

def all_suite_k2v():
    return unittest.TestSuite([SuiteK2V()])

def main():
    unittest.TextTestRunner(verbosity=2).run(all_suite_k2v())
    
if __name__ == '__main__':
    main()

