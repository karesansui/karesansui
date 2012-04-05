# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

from karesansui import __version__, __release__
from karesansui.lib.rest import Rest

class About(Rest):

    def _GET(self, *param, **params):
        self.view.version = __version__
        self.view.release = __release__
        return True

urls = ('/about/?(\.part)$', About,)
