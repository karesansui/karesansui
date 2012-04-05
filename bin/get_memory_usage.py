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

import os
import sys
import time
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection
    from karesansui.lib.utils import gettimeofday
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

class GetMemoryUsage(KssCommand):

    def process(self):
        conn = KaresansuiVirtConnection()
        try:
            guests = conn.search_guests()
    
            nodeinfo = conn.get_nodeinfo()
            
            infos = []
            for guest in guests:
                id = guest.ID()
                if id > -1:
                    name = guest.name()
                    print name
                    info = guest.info()
                    maxMem = info[1]
                    memory = info[2]
                    
                    pcentCurrMem = memory * 100.0 / (nodeinfo["memory"]*1024)
                    pcentMaxMem  = maxMem * 100.0 / (nodeinfo["memory"]*1024)
                    
                    print "%.3f%%" % pcentCurrMem
                    #print pcentMaxMem
                    
            return True
        
        finally:
            conn.close()

if __name__ == "__main__":
    target = GetMemoryUsage()
    sys.exit(target.run())
