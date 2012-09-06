#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *

from karesansui.lib.utils import *

def assert_regexp_matches(text, regexp):
    import re
    if isinstance(regexp, basestring):
        regexp = re.compile(regexp)
    if not regexp.search(text):
        message = '''Regexp didn't match: %r not found in %r''' % (regexp.pattern, text)
        raise AssertionError(message)

class TestList(object):

    def test_sample(self):
        numbers = xrange(10)
        eq_(len(numbers), 10)
        assert max(numbers) == 9
        assert_equal(sum(numbers), 45)

    def test_dotsplit(self):
        string_1 = "foo"
        string_2 = "foo.bar"
        string_3 = "foo.bar.hoge"
        assert_equal(dotsplit(string_1)[0], "foo")
        assert_equal(dotsplit(string_2)[0], "foo")
        assert_equal(dotsplit(string_2)[1], "bar")
        assert_equal(dotsplit(string_3)[0], "foo.bar")
        assert_equal(dotsplit(string_3)[1], "hoge")

    def test_ucfirst(self):
        string_lc = "abcdefg012345-./"
        string_uc = "ABCDEFG012345-./"
        assert_equal(ucfirst(string_lc)[0:4], "Abcd")
        assert_equal(ucfirst(string_uc)[0:4], "ABCD")

    def test_lcfirst(self):
        string_lc = "abcdefg012345-./"
        string_uc = "ABCDEFG012345-./"
        assert_equal(lcfirst(string_lc)[0:4], "abcd")
        assert_equal(lcfirst(string_uc)[0:4], "aBCD")

    def test_next_number(self):
        min = 10
        max = 20
        exclude_numbers = [10,11,12]
        min = 21
        max = 20
        exclude_numbers = [10,11,12]
        assert_equal(next_number(min,max,exclude_numbers), None)

    def test_is_uuid(self):
        uuid = string_from_uuid(generate_uuid())
        assert_equal(is_uuid(uuid), True)

        uuid_1 = generate_uuid()
        uuid_2 = generate_uuid()
        assert uuid_1 != uuid_2

    def test_file_type(self):
        assert_equal(file_type("/etc/hosts"),"ASCII text")
        assert_regexp_matches(file_type("/bin/ls"),"bit LSB executable")

def test_sample():
    numbers = xrange(10)
    assert_equal(len(numbers), 10)
    assert_equal(max(numbers), 9)
    assert_equal(sum(numbers), 45)
