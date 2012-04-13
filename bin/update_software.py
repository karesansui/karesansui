#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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

""" 
<description>

@file:   update_software.py
@author: Kei Funagayama <kei@karesansui-project.info>
@copyright:    

<comment-ja>
Karesansuiパッケージをアップデートする。

 使用方法: update_software.py [オプション]

  オプション:
    --version             プログラムのバージョンを表示
    -h, --help            使用方法を表示
</comment-ja>
<comment-en>
</comment-en>
"""

import os
import sys
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    return optp.parse_args()

def chkopts(opts):
    pass

class UpdateSoftware(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        import karesansui.plus.updater
        yu = karesansui.plus.updater.YumUpdater(karesansui.config)
        try:
            self.up_progress(20)
            yu.refresh()
            self.up_progress(20)
            ret = yu.update()
            self.up_progress(40)
        except:
            raise KssCommandException('failed to update software.')

        if ret:
            self.logger.info('Has been updated.')
            print >>sys.stdout, 'Has been updated.'
        else:
            self.logger.info('Which did not have to be updated..')
            print >>sys.stdout, 'Which did not have to be updated.'

        self.up_progress(10)

        return True

if __name__ == "__main__":
    target = UpdateSoftware()
    sys.exit(target.run())
