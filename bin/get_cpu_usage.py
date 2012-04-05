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

class GetCpuUsage(KssCommand):

    def process(self):
        conn = KaresansuiVirtConnection()
        try:
            guests = conn.search_guests()
    
            infos = []
            for guest in guests:
              id = guest.ID()
              if id > -1:
                name = guest.name()
                info = guest.info()
        
                now = gettimeofday()
                sec = now[0]
                usec = now[1]
                infos.append({"id": id, "cpu_time": info[4], "real_time_sec": long(sec), "real_time_usec": long(usec)})
    
            #print infos
            time.sleep(1.1)
    
            cnt = 0
            for guest in guests:
              id = guest.ID()
              if id > -1:
                name = guest.name()
                print name
                info = guest.info()
    
                now = gettimeofday()
                sec = now[0]
                usec = now[1]
    
                # calculate the usage of cpu
                #print infos[cnt]
                cpu_diff = (info[4] - infos[cnt]["cpu_time"]) / 10000
                #print info[4]
                #print infos[cnt]["cpu_time"]
                #print cpu_diff
    
                #real_diff = 1000 *(long(sec) - infos[cnt]["real_time_sec"]) + (usec - infos[cnt]["real_time_usec"])
                real_diff = ((long(sec) - infos[cnt]["real_time_sec"]) * 1000) + ((usec - infos[cnt]["real_time_usec"]) / 1000);
    
                #real_diff = 1000 *(sec - infos[cnt]["real_time_sec"])
                #real_diff2 = (usec - infos[cnt]["real_time_usec"])
    
                #print "realTime.tv_sec:%10ld" % sec
                #print "infos.real_time.tv_sec:%10ld" % infos[cnt]["real_time_sec"]
                #print "realTime.tv_usec:%10ld" % usec
                #print "infos.real_time.tv_usec:%10ld" % infos[cnt]["real_time_usec"]
                #print "real_diff:%10ld" % real_diff
                #print "cpu_diff:%10ld" % cpu_diff
    
                usage = cpu_diff / float(real_diff);  
                print "%.3f%%" % usage
     
                # print the results
                #printf("%d\t%.3f%\t%lu\t%lu\t%hu\t%0X\t%s\n", id, usage, info.memory / 1024,  
                #info.maxMem / 1024, info.nrVirtCpu, info.state, virDomainGetName(dom));  
                cnt = cnt + 1

                return True
        finally:
            conn.close()

if __name__ == "__main__":
    target = GetCpuUsage()
    sys.exit(target.run())
