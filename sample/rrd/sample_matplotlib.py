#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/lib64/python2.4/site-packages/')
import rrdtool

import datetime
from pylab import *
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter

import time


def millions(x, pos):
    return '%1fM' % (x*1e-6)


data = rrdtool.fetch('memory-used.rrd',
                     "AVERAGE",
                     "-r",
                     "60",
                     "-s",
                     str(int(time.mktime((2010,3,23,16,0,0,1,82,0)))),
                     "-e",
                     str(int(time.mktime((2010,3,23,17,0,0,1,82,0))))
                     )


prop = fm.FontProperties(fname='/home/fukawa/ipamp.otf')
title('テストtest', fontproperties=prop)

#info = rrdtool.info('memory-used.rrd')
#print info

plot(data[2])

formatter = FuncFormatter(millions)
ax = subplot(111)
ax.yaxis.set_major_formatter(formatter)

show()

