#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2012 HDE, Inc.
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

def is_interface_file_exist(rrd_dir, dev):
    ret = True

    rrd_filepath = ("%s/interface/if_packets-%s.rrd" % (rrd_dir, dev),
                    "%s/interface/if_octets-%s.rrd" % (rrd_dir, dev),
                    "%s/interface/if_errors-%s.rrd" % (rrd_dir, dev),
                    )

    for filepath in rrd_filepath:
        if is_readable(filepath) is False:
            ret = False

    return ret

def create_interface_graph(_, lang, graph_dir, rrd_dir, start, end, dev, type):
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = "%s/%s" % (graph_dir, graph_filename)

    rrd_filepath = ("%s/interface/if_%s-%s.rrd" % (rrd_dir, type, dev),
                    )
    # TRANSLATORS:
    #  ネットワークのグラフのタイトル
    graph_title = {
        "packets":"%%s - %s" % (_('Packets').encode("utf-8")),
        "octets":"%%s - %s" % (_('Traffic').encode("utf-8")),
        "errors":"%%s - %s" % (_('Errors').encode("utf-8")),
        }

    # TRANSLATORS:
    #  ネットワークのグラフの縦軸のラベル
    #    packetsは1秒あたりのパケット数
    #    octetsは1秒あたりのバイト数
    #    errorsは1秒あたりのエラーパケット数
    graph_label = {
        "packets":_("Packets / sec").encode("utf-8"),
        "octets":_("Octets / sec").encode("utf-8"),
        "errors":_("Packets / sec").encode("utf-8"),
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

    legend_header = "<tt>             %s        %s        %s        %s</tt>" % (legend_header_label['min'],
                                                                                legend_header_label['max'],
                                                                                legend_header_label['ave'],
                                                                                legend_header_label['last']
                                                                                )

    legend_label = {"rx":_('RX'),
                    "tx":_('TX'),
                    }
    for key in legend_label.keys():
        if re.search(u"[^a-zA-Z0-9]", legend_label[key]):
            legend_label[key] = "</tt>%s<tt>" % (legend_label[key].encode("utf-8"))
        else:
            legend_label[key] = "%s" % (legend_label[key].encode("utf-8"))

    title = "<tt>%s</tt>" % (graph_title[type] % (dev))

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
                         "--start", start,
                         "--end",  end,
                         #"--legend-direction", "bottomup",
                         "DEF:rx=%s:rx:AVERAGE" % (rrd_filepath[0]),
                         "DEF:tx=%s:tx:AVERAGE" % (rrd_filepath[0]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         "AREA:rx#E7EF00:<tt>%s  </tt>" % (legend_label["rx"]),
                         "GPRINT:rx:MIN:<tt>%8.2lf%s</tt>",
                         "GPRINT:rx:MAX:<tt>%8.2lf%s</tt>",
                         "GPRINT:rx:AVERAGE:<tt>%8.2lf%s</tt>",
                         "GPRINT:rx:LAST:<tt>%8.2lf%s</tt>\\n",
                         "STACK:tx#80AA00:<tt>%s  </tt>" % (legend_label["tx"]),
                         "GPRINT:tx:MIN:<tt>%8.2lf%s</tt>",
                         "GPRINT:tx:MAX:<tt>%8.2lf%s</tt>",
                         "GPRINT:tx:AVERAGE:<tt>%8.2lf%s</tt>",
                         "GPRINT:tx:LAST:<tt>%8.2lf%s</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         "LINE1:rx#E7EF00",
                         "STACK:tx#80AA00",
                         )

    return graph_filepath
