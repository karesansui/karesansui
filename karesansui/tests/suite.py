#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""<comment-ja>
全てのテストを実行する。
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

import unittest
from karesansui.tests.lib.file.testk2v import all_suite_k2v
from karesansui.tests.lib.networkaddress import all_suite_networkaddress
from karesansui.tests.lib.utils import all_suite_utils
from karesansui.tests.restapi import all_suite_restapi

ts = unittest.TestSuite()
ts.addTest(all_suite_k2v())
ts.addTest(all_suite_networkaddress())
ts.addTest(all_suite_utils())
ts.addTest(all_suite_restapi())
unittest.TextTestRunner(verbosity=2).run(ts)  
