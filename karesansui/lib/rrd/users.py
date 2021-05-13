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

def create_users_graph(_, lang, graph_dir, rrd_dir, start, end, dev=None, type=None):
    graph_filename = "%s.png" % (generate_phrase(12,'abcdefghijklmnopqrstuvwxyz'))
    graph_filepath = "%s/%s" % (graph_dir, graph_filename)

    rrd_filepath = ("%s/users/users.rrd" % (rrd_dir),
                    )

    for filepath in rrd_filepath:
        if is_readable(filepath) is False:
            return ""

    legend_header_label = {"min":_('Min'),
                           "max":_('Max'),
                           "ave":_('Ave'),
                           "last":_('Last'),
                           }

    for key in list(legend_header_label.keys()):
        if re.search("[^a-zA-Z0-9]", legend_header_label[key]):
            legend_header_label[key] = "</tt>%s<tt>" % (legend_header_label[key].encode("utf-8"))
        else:
            legend_header_label[key] = "%s" % (legend_header_label[key].encode("utf-8"))

    legend_header = "<tt>                 %s       %s       %s       %s</tt>" % (legend_header_label['min'],
                                                                                legend_header_label['max'],
                                                                                legend_header_label['ave'],
                                                                                legend_header_label['last']
                                                                                )
    # TRANSLATORS:
    #  ユーザ数のグラフのタイトル
    title = _('Users Logged In')
    if re.search("[^a-zA-Z0-9_\-\.]", title):
        title = "%s" % (title.encode("utf-8"))
    else:
        title = "<tt>%s</tt>" % (title.encode("utf-8"))

    created_label = _('Graph created')
    if re.search("[^a-zA-Z0-9 ]", created_label):
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
                         # TRANSLATORS:
                         #   ユーザ数のグラフの縦軸のラベル
                         "--vertical-label", _('Users ').encode("utf-8"),
                         "--start", start,
                         "--end",  end,
                         #"--legend-direction", "bottomup",
                         "DEF:users=%s:users:AVERAGE" % (rrd_filepath[0]),
                         "COMMENT:%s\\r" % legend_footer,
                         "COMMENT:<tt>---------------------------------------------------------------------------</tt>\\n",
                         # TRANSLATORS:
                         #   ユーザ数のグラフの凡例
                         "AREA:users#80AA00:<tt>%s    </tt>" % (_('Users').encode("utf-8")),
                         "GPRINT:users:MIN:<tt>%8.2lf</tt>",
                         "GPRINT:users:MAX:<tt>%8.2lf</tt>",
                         "GPRINT:users:AVERAGE:<tt>%8.2lf</tt>",
                         "GPRINT:users:LAST:<tt>%8.2lf</tt>\\n",
                         "COMMENT:%s\\n" % (legend_header),
                         "COMMENT: \\n",
                         )

    return graph_filepath
