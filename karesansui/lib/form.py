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
