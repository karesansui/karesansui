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

from karesansui.lib.checker import Checker, \
    CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX
from karesansui.lib.const import PAGE_MIN_SIZE, PAGE_MAX_SIZE
from karesansui.lib.utils import is_param

def validates_page(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    if is_param(obj.input, 'p'):
        check = checker.check_number(
                _('Page Number'),
                obj.input.p,
                CHECK_EMPTY | CHECK_VALID | CHECK_MIN | CHECK_MAX,
                min = PAGE_MIN_SIZE,
                max = PAGE_MAX_SIZE,
                ) and check

    obj.view.alert = checker.errors
    return check

class Pager(object):
    """<comment-ja>
    karesansui.db.model.Modelのリストを任意の数で表示する
    ページを作成するクラス。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    def __init__(self, target, now, limit):
        """<comment-ja>
        1ページに表示する対象の数をlimitで指定します。
        表示するページ番号をnowで指定します。
        @param target: ページで区切る対象のリスト
        @type target: [karesansui.db.model.Model...]
        @param now: 表示するページ番号
        @type now: int
        @param limit: 1ページに表示する対象の数
        @type limit: int 
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.now = now
        self.limit = limit
        self.total = len(target)
        self.page = self.total / limit
        self.rpage = self.total % limit
        self.start = self.now * self.limit
        self.end = (self.now * self.limit) + self.limit

        if 0 < self.rpage:
            self.page += 1

        self.displays = target[self.start:self.end]

        page_list_size = 6 

        if 0 <= self.now-3:
            self.lnow = self.now - 3
            page_list_size -= 3
        else:
            self.lnow = 0
            page_list_size -= now

        if self.now+3 <= self.page:
            self.rnow = self.now + page_list_size
            if self.page < self.rnow:
                self.rnow = self.page
        else:
            self.rnow = self.page

        page_list = []
        for x in range(int(self.lnow), int(self.rnow)):
            page_list.append(x)
        self.page_list = page_list

    def get_page_list(self):
        """<comment-ja>
        ページ番号のリストを取得する。
        @return: ページ番号のリスト
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return self.page_list

    def is_now_page(self, num):
        """<comment-ja>
        numが現在のページか
        @param num: ページ番号
        @type num: int
        @return: bool
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if num == self.now:
            return True
        else:
            return False

    def get_next_page(self):
        """<comment-ja>
        次のページを取得する。
        @return: 次のページのページ番号
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return self.now + 1

    def get_prev_page(self):
        """<comment-ja>
        前のページを取得する。
        @return: 前のページのページ番号
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return self.now - 1

    def exist_next_page(self):
        """<comment-ja>
        次のページが存在するか
        @return: bool
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.now+1 < self.page:
            return True
        else:
            return False

    def exist_prev_page(self):
        """<comment-ja>
        前のページが存在するか
        @return: bool
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if 0 <= self.now - 1:
            return True
        else:
            return False

    def exist_now_page(self):
        """<comment-ja>
        表示するページが存在するか
        @return: bool
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.now < self.page:
            return True
        else:
            return False

    def get_displays(self):
        """<comment-ja>
        1ページに表示する対象のリストを取得する
        @return: 1ページに表示する対象のリスト
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return self.displays

    def get_start(self):
        """<comment-ja>
        1ページに表示する最初の対象の順番を取得する
        @return: 1ページに表示する最初の対象の順番
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.total == 0:
            return 0
        else:
            return self.start + 1

    def get_end(self):
        """<comment-ja>
        1ページに表示する最後の対象の順番を取得する
        @return: 1ページに表示する最後の対象の順番
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if self.end < self.total:
            return self.end
        else:
            return self.total

    def get_total(self):
        """<comment-ja>
        全対象の数を取得する
        @return: ページ番号のリスト
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        return self.total
