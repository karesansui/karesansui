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

"""<comment-ja>
国際化したい文字列を定義します。
 例) 動的に文字列を定義した場合など
</comment-ja>
<comment-en>
</comment-en>
"""

try:
    import karesansui
    import gettext
    gettext.install('messages', karesansui.dirname + "/locale")
except (ImportError,AttributeError,IOError):
    def _(msg):
        return msg

ja_JP = _("ja_JP")
en_US = _("en_US")
de_DE = _("de_DE")
es_ES = _("es_ES")
fr_FR = _("fr_FR")
it_IT = _("it_IT")
ko_KR = _("ko_KR")
pt_BR = _("pt_BR")
zh_CN = _("zh_CN")
