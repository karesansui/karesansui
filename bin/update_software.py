#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
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
