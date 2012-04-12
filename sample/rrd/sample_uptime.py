#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/lib/python2.6/')
import rrdtool

from rrd_const import RRD_DIR, START_TIME, END_TIME

data = rrdtool.graph('uptime_graph.gif',
                     "--font", "DEFAULT:0:IPAexGothic",
                     "--title", "uptimeの情報",
                     "--vertical-label", "sec",
                     "--width", "500",
                     "--height", "200",
                     "--start", START_TIME,
                     "--end",  END_TIME,
#                     "--legend-direction", "bottomup",
                     "DEF:uptime=" + RRD_DIR + "uptime/uptime.rrd:value:AVERAGE",
                     "VDEF:max=uptime,MAXIMUM",
                     "VDEF:min=uptime,MINIMUM",
                     "VDEF:average=uptime,AVERAGE",
                     "AREA:uptime#DDDDDD",
                     "LINE1:uptime#FF6622:Current",
                     "GPRINT:uptime:LAST:%6.2lf Last\\n",
                     "HRULE:max#FF0000:Maximum:dashes",
                     "GPRINT:uptime:MAX:%6.2lf max\\n",
                     "HRULE:min#FFFF00:Minimum:dashes",
                     "GPRINT:uptime:MIN:%6.2lf min\\n",
                     "HRULE:average#0044FF:Average:dashes",
                     "GPRINT:uptime:AVERAGE:%6.2lf ave\\n",
                     )
