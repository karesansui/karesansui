#!/usr/bin/env python
# -*- coding: utf_8 -*-

import sys
import os
import unittest
import re
import web

from paste.fixture import TestApp
#from nose.tools import *

import logging
import karesansui
import karesansui.urls

username = "ja@localhost"
password = "password"

class TestRestAPI(unittest.TestCase):

    def setUp(self):
        middleware = []
        self.logger = logging.getLogger('restapi')
        urls = karesansui.urls.urls
        app = web.application(urls, globals(), autoreload=False)

        from karesansui.app import load_sqlalchemy_karesansui,load_sqlalchemy_pysilhouette
        app.add_processor(load_sqlalchemy_karesansui)
        app.add_processor(load_sqlalchemy_pysilhouette)

        self.prefix = ""
        if karesansui.config['application.url.prefix']:
            mapping = (karesansui.config['application.url.prefix'],  app)
            app = web.subdir_application(mapping)
            self.prefix = karesansui.config['application.url.prefix']

        self.app = TestApp(app.wsgifunc(*middleware))

        self.headers = {}
        if username != None and password != None:
            from base64 import b64encode
            base64string =b64encode("%s:%s" % (username, password))
            self.headers = {"Authorization": "Basic %s" % base64string}

        return True

    def tearDown(self):
        return True

    def test_dummy(self):
        self.assertEqual(True,True)
 
    def test_get_index(self):
        r = self.app.get("%s/" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('Now Loading')

    def test_get_host_1_index(self):
        r = self.app.get("%s/host/1/" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('Now Loading')

    def test_get_host_1_json(self):
        r = self.app.get("%s/host/1.json" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('other_url')

    def test_get_host_1_guest_2_index(self):
        r = self.app.get("%s/host/1/guest/2/" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('Now Loading')

    def test_get_host_1_guest_2_json(self):
        r = self.app.get("%s/host/1/guest/2.json" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('other_url')

    def test_post_host_1_guest(self):

        params = {}
        params['domain_name'] = 'foobar'
        params['m_name'] = 'foobar'
        params['icon_filename'] = ''
        params['m_hypervisor'] = '1'
        params['note_title'] = 'title'
        params['note_value'] = 'value'
        params['tags'] = ''
        params['nic_type'] = 'phydev'
        params['phydev'] = 'xenbr0'
        params['virnet'] = 'default'
        params['xen_disk_size'] = '4096'
        params['xen_extra'] = ''
        params['xen_initrd'] = '/var/ftp/images/xen/initrd.img'
        params['xen_kernel'] = '/var/ftp/images/xen/vmlinuz'
        params['xen_mac'] = '00:16:3e:4e:4d:e2'
        params['xen_mem_size'] = '256'
        params['xen_graphics_port'] = '5910'
        upload_files=None

        r = self.app.post("%s/host/1/guest.part" % self.prefix,params=params,headers=self.headers,upload_files=upload_files)
        assert_equal(r.status, 200)
        r.mustcontain('other_url')

    def test_del_host_1_guest_2(self):
        r = self.app.delete("%s/host/1/guest/2" % self.prefix,headers=self.headers)
        assert_equal(r.status, 200)
        r.mustcontain('other_url')

class SuiteRestAPI(unittest.TestSuite):
    def __init__(self):
        tests = ['test_dummy',
                 'test_get_index',
                 'test_get_host_1_index',
                 'test_get_host_1_json',
                 'test_get_host_1_guest_2_index',
                 'test_get_host_1_guest_2_json',
                 'test_post_host_1_guest',
                 ]
        unittest.TestSuite.__init__(self,map(TestRestAPI, tests))

def all_suite_restapi():
    return unittest.TestSuite([SuiteRestAPI()])

def main():
    unittest.TextTestRunner(verbosity=2).run(all_suite_restapi())
    
if __name__ == '__main__':
    main()

