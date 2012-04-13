#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

import re
import datetime
import rrdtool
import karesansui
from karesansui.lib.const import GRAPH_COMMON_PARAM, DEFAULT_LANGS
from karesansui.lib.utils import is_readable, generate_phrase

def is_cpu_file_exist(rrd_dir, dev):
    ret = True
    dev = str(dev)

    rrd_filepath = ("%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "idle"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "interrupt"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "nice"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "user"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "wait"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "system"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "softirq"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, dev, "steal"),
                    )

    for filepath in rrd_filepath:
        if is_readable(filepath) is False:
            ret = False

    return ret

def create_cpu_graph(_, lang, graph_dir, rrd_dir, start, end, dev=0, type=None):
    cpu_number = str(dev)
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = "%s/%s" % (graph_dir, graph_filename)

    rrd_filepath = ("%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "idle"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "interrupt"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "nice"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "user"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "wait"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "system"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "softirq"),
                    "%s/cpu-%s/cpu-%s.rrd" % (rrd_dir, cpu_number, "steal"),
                    )

    for filename in rrd_filepath:
        if is_readable(filename) is False:
            return ""

    legend_header_label = {"min":_('Min'),
                           "max":_('Max'),
                           "ave":_('Ave'),
                           "last":_('Last'),
                           }

    for key in legend_header_label.keys():
        if re.search(u"[^a-zA-Z0-9]", legend_header_label[key]):
            legend_header_label[key] = "</tt>%s<tt>" % (legend_header_label[key].encode("utf-8"))
        else:
            legend_header_label[key] = "%s" % (legend_header_label[key].encode("utf-8"))

    legend_header = "<tt>                     %s       %s       %s       %s</tt>" % (legend_header_label['min'],
                                                                                     legend_header_label['max'],
                                                                                     legend_header_label['ave'],
                                                                                     legend_header_label['last']
                                                                                     )
    title = "<tt>CPU-%s</tt>" % (str(cpu_number))

    created_label = _('Graph created')
    if re.search(u"[^a-zA-Z0-9 ]", created_label):
        created_label = "</tt>%s<tt>" % (created_label.encode("utf-8"))
    else:
        created_label = "%s" % (created_label.encode("utf-8"))

    created_time = "%s" % (datetime.datetime.today().strftime(DEFAULT_LANGS[lang]['DATE_FORMAT'][1]))
    created_time = re.sub(r':', '\:', created_time)

    legend_footer = "<tt>%s \: %s</tt>" % (created_label, created_time)

    data = rrdtool.graph(graph_filepath,
    "--imgformat", "PNG",
    "--font", "TITLE:0:IPAexGothic",
    "--font", "LEGEND:0:IPAexGothic",
    "--pango-markup",
    "--width", "550",
    "--height", "350",
    "--full-size-mode",
    "--color", "BACK#FFFFFF",
    "--color", "CANVAS#FFFFFF",
    "--color", "SHADEA#FFFFFF",
    "--color", "SHADEB#FFFFFF",
    "--color", "GRID#DDDDDD",
    "--color", "MGRID#CCCCCC",
    "--color", "FONT#555555",
    "--color", "FRAME#FFFFFF",
    "--color", "ARROW#FFFFFF",
                         "--title", title,
                         "--vertical-label", "jiffies",
                         "--units-length", "2",
                         "--upper-limit", "100",
                         "--lower-limit", "0",
                         "--rigid",
                         "--start", start,
                         "--end",  end,
                         #"--legend-direction", "bottomup",
                         "DEF:idle=%s:value:AVERAGE" % (rrd_filepath[0]),
                         "DEF:interrupt=%s:value:AVERAGE" % (rrd_filepath[1]),
                         "DEF:nice=%s:value:AVERAGE" % (rrd_filepath[2]),
                         "DEF:user=%s:value:AVERAGE" % (rrd_filepath[3]),
                         "DEF:wait=%s:value:AVERAGE" % (rrd_filepath[4]),
                         "DEF:system=%s:value:AVERAGE" % (rrd_filepath[5]),
                         "DEF:softirq=%s:value:AVERAGE" % (rrd_filepath[6]),
                         "DEF:steal=%s:value:AVERAGE" % (rrd_filepath[7]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         # TRANSLATORS:
                         #  CPUのグラフの凡例
                         #  日本語にした場合は表示が崩れますが、後で直すのでそのままで大丈夫です
                         "AREA:steal#FDFF6A:<tt>%s       </tt>" % (_('Steal').encode("utf-8")),
                         "GPRINT:steal:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:steal:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:steal:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:steal:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:interrupt#F7FF13:<tt>%s   </tt>" % (_('Interrupt').encode("utf-8")),
                         "GPRINT:interrupt:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:interrupt:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:interrupt:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:interrupt:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:softirq#E7EF00:<tt>%s     </tt>" % (_('SoftIRQ').encode("utf-8")),
                         "GPRINT:softirq:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:softirq:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:softirq:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:softirq:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:system#B5F100:<tt>%s      </tt>" % (_('System').encode("utf-8")),
                         "GPRINT:system:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:system:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:system:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:system:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:wait#B3EF00:<tt>%s   </tt>" % (_('Wait - IO').encode("utf-8")),
                         "GPRINT:wait:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:wait:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:wait:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:wait:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:user#95C700:<tt>%s       </tt>" % (_('User').encode("utf-8")),
                         "GPRINT:user:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:user:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:user:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:user:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:nice#80AA00:<tt>%s        </tt>" % (_('Nice').encode("utf-8")),
                         "GPRINT:nice:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:nice:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:nice:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:nice:LAST:<tt>%8.2lf</tt>\\n",
                         "STACK:idle#FFFFFF:<tt>%s        </tt>" % (_('Idle').encode("utf-8")),
                         "GPRINT:idle:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:idle:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:idle:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:idle:LAST:<tt>%8.2lf</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         )

    return graph_filepath
