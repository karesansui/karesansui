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

from web.form import *

class Label(Input):
    """<comment-ja>
    webpy#formの拡張Labelクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    def render(self, shownote=True):
        x = '<label for="_%s" ' % net.websafe(self.name)
        x += self.addatts()
        x += ' >'   
        if self.value: x += net.websafe(self.value)
        x += '</label>'
        if shownote:
            x += self.rendernote(self.note)
        return x

class CButton(Button):
    """<comment-ja>
    webpy#formの拡張Buttonクラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    def __init__(self, name, *validators, **attrs):
        super(Button, self).__init__(name, *validators, **attrs)
        self.description = ""
              
    def render(self):
        safename = net.websafe(self.name)
        safevalue = net.websafe(self.value)
        x = '<button name="%s"%s>%s</button>' % (safename, self.addatts(), safevalue)
        x += self.rendernote(self.note)
        return x
