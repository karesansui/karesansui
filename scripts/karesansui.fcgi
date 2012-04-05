#!/usr/bin/python
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
__license__ = 'GPL'

import os
import sys

def main():
    if os.environ.get('SEARCH_PATH'):
        for y in [x.strip() for x in os.environ.get('SEARCH_PATH').split(':') if x]: 
            if (y in sys.path) is False: sys.path.insert(0, y)

    if os.environ.has_key('FCGI') is False:
        os.environ['FCGI'] = '1'

    import karesansui, karesansui.app
    karesansui.app.main()

if __name__ == "__main__":
    sys.exit(main())
