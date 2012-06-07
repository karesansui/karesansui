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

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
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
