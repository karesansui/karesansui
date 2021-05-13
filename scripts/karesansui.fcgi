#!/usr/bin/python
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
[Environ]
SEARCH_PATH={Please specify the folder path for karesansui and pysilhouette.}
 - Example) /usr/lib/python,
 - Tips) Separate paths with commas for multiple paths.

FCGI={Please set any value.}
 - Example) 1

KARESANSUI_CONF={Please set the path to the configuration file.}
 - Example) /etc/karesansui/application.conf 

[command]
python karesansui.fcgi
"""

__author__ = "Kei Funagayama <kei.funagayama@hde.co.jp>"
__copyright__ = 'Copyright (C) 2009-2010 Karesansui Project'
__license__ = 'MIT'

import os
import sys

def main():
    if os.environ.get('SEARCH_PATH'):
        for y in [x.strip() for x in os.environ.get('SEARCH_PATH').split(':') if x]: 
            if (y in sys.path) is False: sys.path.insert(0, y)

    if os.environ.get('FCGI') is None:
        os.environ['FCGI'] = '1'

    import karesansui, karesansui.app
    karesansui.app.main()

if __name__ == "__main__":
    sys.exit(main())
