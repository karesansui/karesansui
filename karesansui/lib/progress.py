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

import sys
import time

try:
    import urlgrabber.progress as progress
except:
    raise

class ProgressMeter(progress.TextMeter):

    def __init__(self, command_object=None, quiet=False, fo=sys.stderr):
        progress.TextMeter.__init__(self)
        self.fo = fo
        self.quiet = quiet
        self.command_object = command_object

    def update(self, amount_read, now=None):
        if now is None:
            now = time.time()
        if (now >= self.last_update_time + self.update_period) or not self.last_update_time:
            self.re.update(amount_read, now)
            self.last_amount_read = amount_read
            self.last_update_time = now
            if self.quiet is False:
                self._do_update(amount_read, now)
            try:
                self.command_object.up_progress(1)
            except:
                pass

    def end(self, amount_read, now=None):
        if now is None:
            now = time.time()
        self.re.update(amount_read, now)
        self.last_amount_read = amount_read
        self.last_update_time = now
        if self.quiet is False:
            self._do_end(amount_read, now)
        try:
            self.command_object.up_progress(1)
        except:
            pass

