#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
