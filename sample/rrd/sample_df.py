#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/lib/python2.6/')
import rrdtool

from rrd_const import RRD_DIR, START_TIME, END_TIME

dev = "mapper_VolGroup00-LogVol00"

data = rrdtool.graph('df_graph.gif',
                     "--font", "DEFAULT:0:IPAexGothic",
                     "--title", dev + "の情報",
                     "--vertical-label", "Byte",
                     "--lower-limit", "0",
                     "--rigid",
                     "--width", "500",
                     "--height", "200",
                     "--start", START_TIME,
                     "--end",  END_TIME,
#                     "--legend-direction", "bottomup",
                     "DEF:used=" + RRD_DIR + "df/df-" + dev + ".rrd:used:AVERAGE",
                     "DEF:free=" + RRD_DIR + "df/df-" + dev + ".rrd:free:AVERAGE",
                     "AREA:used#FF9999:Used",
                     "GPRINT:used:MIN:%6.2lf%s Min, ",
                     "GPRINT:used:MAX:%6.2lf%s Max, ",
                     "GPRINT:used:AVERAGE:%6.2lf%s Ave, ",
                     "GPRINT:used:LAST:%6.2lf%s Last\\n",
                     "STACK:free#99FF99:Free",
                     "GPRINT:free:MIN:%6.2lf%S Min, ",
                     "GPRINT:free:MAX:%6.2lf%S Max, ",
                     "GPRINT:free:AVERAGE:%6.2lf%S Ave, ",
                     "GPRINT:free:LAST:%6.2lf%S Last\\n",
                     "LINE1:used#FF0000",
                     "STACK:free#00FF00",
                     )

