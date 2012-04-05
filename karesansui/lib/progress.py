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

