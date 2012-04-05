#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

import re
import datetime
import rrdtool
import karesansui
from karesansui.lib.const import GRAPH_COMMON_PARAM, DEFAULT_LANGS
from karesansui.lib.utils import is_readable, generate_phrase

def create_load_graph(_, lang, graph_dir, rrd_dir, start, end, dev=None, type=None):
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = "%s/%s" % (graph_dir, graph_filename)

    rrd_filepath = ("%s/load/load.rrd" % (rrd_dir),
                    )

    for filepath in rrd_filepath:
        if is_readable(filepath) is False:
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

    legend_header = "<tt>                    %s       %s       %s       %s</tt>" % (legend_header_label['min'],
                                                                                       legend_header_label['max'],
                                                                                       legend_header_label['ave'],
                                                                                       legend_header_label['last']
                                                                                       )

    title = _('Load Average')
    if re.search(u"[^a-zA-Z0-9_\-\. ]", title):
        title = "%s" % (title.encode("utf-8"))
    else:
        title = "<tt>%s</tt>" % (title.encode("utf-8"))

    # TRANSLATORS:
    #   ロードアベレージのグラフの凡例
    legend = {"1m":_('1m Average'),
              "5m":_('5m Average'),
              "15m":_('15m Average'),
              }
    for key in legend.keys():
        if re.search(u"[^a-zA-Z0-9_\-\. ]", legend[key]):
            legend[key] = "</tt>%s   <tt>" % (legend[key].encode("utf-8"))
        else:
            legend[key] = "%s" % (legend[key].encode("utf-8"))

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
                         "--vertical-label", _('System load').encode("utf-8"),
                         "--start", start,
                         "--end",  end,
                         "--units-exponent", "0",
                         #"--legend-direction", "bottomup",
                         "DEF:shortterm=%s:shortterm:AVERAGE" % (rrd_filepath[0]),
                         "DEF:midterm=%s:midterm:AVERAGE" % (rrd_filepath[0]),
                         "DEF:longterm=%s:longterm:AVERAGE" % (rrd_filepath[0]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         "LINE:shortterm#E7EF00:<tt>%s </tt>" % (legend["1m"]),
                         "GPRINT:shortterm:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:shortterm:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:shortterm:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:shortterm:LAST:<tt>%8.2lf</tt>\\n",
                         "LINE:midterm#B3EF00:<tt>%s </tt>" % (legend["5m"]),
                         "GPRINT:midterm:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:midterm:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:midterm:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:midterm:LAST:<tt>%8.2lf</tt>\\n",
                         "LINE:longterm#80AA00:<tt>%s</tt>" % (legend["15m"]),
                         "GPRINT:longterm:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:longterm:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:longterm:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:longterm:LAST:<tt>%8.2lf</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         )

    return graph_filepath
