#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/lib/python2.6/')
import rrdtool

from rrd_const import RRD_DIR, START_TIME, END_TIME

data = rrdtool.graph('memory_graph.gif',
                     "--font", "DEFAULT:0:IPAexGothic",
                     "--title", "メモリの情報",
                     "--vertical-label", "byte",
#                     "--upper-limit", "536870912",
                     "--lower-limit", "0",
                     "--rigid",
                     "--width", "500",
                     "--height", "200",
                     "--start", START_TIME,
                     "--end",  END_TIME,
                     "--legend-direction", "bottomup",
                     "DEF:free=" + RRD_DIR + "memory/memory-free.rrd:value:AVERAGE",
                     "DEF:cached=" + RRD_DIR + "memory/memory-cached.rrd:value:AVERAGE",
                     "DEF:buffered=" + RRD_DIR + "memory/memory-buffered.rrd:value:AVERAGE",
                     "DEF:used=" + RRD_DIR + "memory/memory-used.rrd:value:AVERAGE",
                     "AREA:used#FFAAAA:used\t",
                     "GPRINT:used:MIN:%6.1lf %s\t",
                     "GPRINT:used:MAX:%6.1lf %s\t",
                     "GPRINT:used:AVERAGE:%6.1lf %s\t",
                     "GPRINT:used:LAST:%6.1lf %s\\n",
                     "STACK:buffered#FFDDAA:buffered",
                     "GPRINT:buffered:MIN:%6.1lf %s\t",
                     "GPRINT:buffered:MAX:%6.1lf %s\t",
                     "GPRINT:buffered:AVERAGE:%6.1lf %s\t",
                     "GPRINT:buffered:LAST:%6.1lf %s\\n",
                     "STACK:cached#AAAAFF:cached",
                     "GPRINT:cached:MIN:%6.1lf %s\t",
                     "GPRINT:cached:MAX:%6.1lf %s\t",
                     "GPRINT:cached:AVERAGE:%6.1lf %s\t",
                     "GPRINT:cached:LAST:%6.1lf %s\\n",
                     "STACK:free#AAFFAA:free\t",
                     "GPRINT:free:MIN:%6.1lf %s\t",
                     "GPRINT:free:MAX:%6.1lf %s\t",
                     "GPRINT:free:AVERAGE:%6.1lf %s\t",
                     "GPRINT:free:LAST:%6.1lf %s\\n",
#                     "COMMENT:色                      最小            最大          平均            最新\\n",
                     "COMMENT:色\t\t最小\t最大\t平均\t最新\\n",
                     "COMMENT: \\n",
                     "LINE1:used#FF0000",
                     "STACK:buffered#DD9900",
                     "STACK:cached#0000FF",
                     "STACK:free#00FF00",
                     )
