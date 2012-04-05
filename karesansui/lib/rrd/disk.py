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

def is_disk_file_exist(rrd_dir, dev):
    ret = True

    rrd_filepath = ("%s/disk-%s/disk_merged.rrd" % (rrd_dir, dev),
                    "%s/disk-%s/disk_octets.rrd" % (rrd_dir, dev),
                    "%s/disk-%s/disk_ops.rrd" % (rrd_dir, dev),
                    "%s/disk-%s/disk_time.rrd" % (rrd_dir, dev),
                    )

    for filepath in rrd_filepath:
        if is_readable(filepath) is False:
            ret = False

    return ret

def create_disk_graph(_, lang, graph_dir, rrd_dir, start, end, dev, type):
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = "%s/%s" % (graph_dir, graph_filename)

    rrd_filepath = ("%s/disk-%s/disk_%s.rrd" % (rrd_dir, dev, type),
                    )

    # TRANSLATORS:
    #  ディスク性能のグラフの縦軸のラベル
    #  /proc/diskstatsの値をとってきているらしいです
    #  よく分からないので、公式HPの説明をコピペしておきます
    #
    #    "merged" are the number of operations, that could be merged into other, already queued operations, i. e. one physical disk access served two or more logical operations. Of course, the higher that number, the better.
    #    "time" is the average time an I/O-operation took to complete. Since this is a little messy to calculate take the actual values with a grain of salt.
    graph_label = {
        "merged":_("Merged Ops / sec").encode("utf-8"),
        "octets":_("Bytes / sec").encode("utf-8"),
        "ops":_("Ops / sec").encode("utf-8"),
        "time":_("Seconds / op").encode("utf-8"),
        }

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

    legend_header = "<tt>                  %s        %s        %s        %s</tt>" % (legend_header_label['min'],
                                                                                     legend_header_label['max'],
                                                                                     legend_header_label['ave'],
                                                                                     legend_header_label['last']
                                                                                     )

    legend_label = {"read":_('Read'),
                    "write":_('Write'),
                    }
    for key in legend_label.keys():
        if re.search(u"[^a-zA-Z0-9]", legend_label[key]):
            legend_label[key] = "</tt>%s<tt>" % (legend_label[key].encode("utf-8"))
        else:
            if key == "read":
                legend_label[key] = "%s " % (legend_label[key].encode("utf-8"))
            else:
                legend_label[key] = "%s" % (legend_label[key].encode("utf-8"))

    title = "<tt>%s/disk_%s</tt>" % (dev,type)

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
                         "--vertical-label", graph_label[type],
                         "--lower-limit", "0",
                         "--rigid",
                         "--start", start,
                         "--end",  end,
                         #"--legend-direction", "bottomup",
                         "DEF:read=%s:read:AVERAGE" % (rrd_filepath[0]),
                         "DEF:write=%s:write:AVERAGE" % (rrd_filepath[0]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         "AREA:read#E7EF00:<tt>%s    </tt>" % legend_label["read"],
                         "GPRINT:read:MIN:<tt>%8.2lf%s</tt>",
                         "GPRINT:read:MAX:<tt>%8.2lf%s</tt>",
                         "GPRINT:read:AVERAGE:<tt>%8.2lf%s</tt>",
                         "GPRINT:read:LAST:<tt>%8.2lf%s</tt>\\n",
                         "STACK:write#80AA00:<tt>%s    </tt>" % legend_label["write"],
                         "GPRINT:write:MIN:<tt>%8.2lf%s</tt>",
                         "GPRINT:write:MAX:<tt>%8.2lf%s</tt>",
                         "GPRINT:write:AVERAGE:<tt>%8.2lf%s</tt>",
                         "GPRINT:write:LAST:<tt>%8.2lf%s</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         "LINE1:read#E7EF00",
                         "STACK:write#80AA00",
                         )

    return graph_filepath
