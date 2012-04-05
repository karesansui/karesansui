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

def create_memory_graph(_, lang, graph_dir, rrd_dir, start, end, dev=None, type=None):
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = '%s/%s' % (graph_dir, graph_filename)

    rrd_filepath = ("%s/memory/memory-%s.rrd" % (rrd_dir, "free"),
                    "%s/memory/memory-%s.rrd" % (rrd_dir, "cached"),
                    "%s/memory/memory-%s.rrd" % (rrd_dir, "buffered"),
                    "%s/memory/memory-%s.rrd" % (rrd_dir, "used"),
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

    legend_header = "<tt>                      %s         %s         %s         %s</tt>" % (legend_header_label['min'],
                                                                                            legend_header_label['max'],
                                                                                            legend_header_label['ave'],
                                                                                            legend_header_label['last']
                                                                                            )

    title = _('Memory')
    if re.search(u"[^a-zA-Z0-9_\-\. ]", title):
        title = "%s" % (title.encode("utf-8"))
    else:
        title = "<tt>%s</tt>" % (title.encode("utf-8"))

    legend = {"used"     : _('Used'),
              "buffered" : _('Buffered'),
              "cached"   : _('Cached'),
              "free"     : _('Free'),
              }

    reg = re.compile(u"[^a-zA-Z0-9_\-\. ]")
    for key in legend.keys():
        if key == "used":
            if reg.search(legend[key]):
                legend[key] = "</tt>%s　　　<tt>    " % (legend[key].encode("utf-8"))
            else:
                legend[key] = "%s        " % (legend[key].encode("utf-8"))
        elif key == "buffered":
            if reg.search(legend[key]):
                legend[key] = "</tt>%s　<tt>     " % (legend[key].encode("utf-8"))
            else:
                legend[key] = "%s    " % (legend[key].encode("utf-8"))
        elif key == "cached":
            if reg.search(legend[key]):
                legend[key] = "</tt>%s<tt>     " % (legend[key].encode("utf-8"))
            else:
                legend[key] = "%s      " % (legend[key].encode("utf-8"))
        elif key == "free":
            if reg.search(legend[key]):
                legend[key] = "</tt>%s　　　<tt>     " % (legend[key].encode("utf-8"))
            else:
                legend[key] = "%s        " % (legend[key].encode("utf-8"))
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
                         "--vertical-label", _('Bytes').encode("utf-8"),
                         "--lower-limit", "0",
                         "--rigid",
                         "--start", start,
                         "--end",  end,
                         #"--legend-direction", "bottomup",
                         "DEF:free=%s:value:AVERAGE" % (rrd_filepath[0]),
                         "DEF:cached=%s:value:AVERAGE" % (rrd_filepath[1]),
                         "DEF:buffered=%s:value:AVERAGE" % (rrd_filepath[2]),
                         "DEF:used=%s:value:AVERAGE" % (rrd_filepath[3]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         # TRANSLATORS:
                         #  メモリのグラフの項目名
                         #  日本語にした場合は表示が崩れますが、後で直すのでそのままで大丈夫です
                         "AREA:used#80AA00:<tt>%s</tt>" % (legend['used']),
                         "GPRINT:used:MIN:<tt>%8.1lf %s</tt>",
                         "GPRINT:used:MAX:<tt>%8.1lf %s</tt>",
                         "GPRINT:used:AVERAGE:<tt>%8.1lf %s</tt>",
                         "GPRINT:used:LAST:<tt>%8.1lf %s</tt>\\n",
                         "STACK:buffered#E7EF00:<tt>%s</tt>" % (legend['buffered']),
                         "GPRINT:buffered:MIN:<tt>%8.1lf %s</tt>",
                         "GPRINT:buffered:MAX:<tt>%8.1lf %s</tt>",
                         "GPRINT:buffered:AVERAGE:<tt>%8.1lf %s</tt>",
                         "GPRINT:buffered:LAST:<tt>%8.1lf %s</tt>\\n",
                         "STACK:cached#B3EF00:<tt>%s</tt>" % (legend['cached']),
                         "GPRINT:cached:MIN:<tt>%8.1lf %s</tt>",
                         "GPRINT:cached:MAX:<tt>%8.1lf %s</tt>",
                         "GPRINT:cached:AVERAGE:<tt>%8.1lf %s</tt>",
                         "GPRINT:cached:LAST:<tt>%8.1lf %s</tt>\\n",
                         "STACK:free#FFFFFF:<tt>%s</tt>" % (legend['free']),
                         "GPRINT:free:MIN:<tt>%8.1lf %s</tt>",
                         "GPRINT:free:MAX:<tt>%8.1lf %s</tt>",
                         "GPRINT:free:AVERAGE:<tt>%8.1lf %s</tt>",
                         "GPRINT:free:LAST:<tt>%8.1lf %s</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         )

    return graph_filepath
