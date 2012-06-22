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

"""
@authors: Taizo ITO <taizo@karesansui-project.info>
          Keisuke Fukawa <keisuke@karesansui-project.info>
          Kei Funagayama <kei@karesansui-project.info>
          Junichi Shinohara <junichi@karesansui-project.info>
          Kazuya Hayashi <kazuya@karesansui-project.info>
          Kazuhiro Ogura <rgoura@karesansui-project.info>
"""

__author__ = "Kei Funagayama <kei@karesansui-project.info>"
__version__ = '3.0'
__release__ = '1'
__app__ = 'karesansui'

import os

config = None
"""<comment-ja>
@param config: 起動時に読み込まれた設定ファイルの情報
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

sheconf = None
"""<comment-ja>
@param config: 起動時に読み込まれたPySilhouette設定ファイルの情報
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

dirname=os.path.dirname(__file__)

class KaresansuiException(Exception):
    """
    <comment-ja>
    Karesansuiシステム共通例外クラス
    Karesansuiシステムで使用される例外はすべてこのクラスを継承しています。
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    pass

class KaresansuiGadgetException(KaresansuiException):
    pass

class KaresansuiDBException(KaresansuiException):
    pass

class KaresansuiLibException(KaresansuiException):
    pass

class KaresansuiTemplateException(KaresansuiException):
    pass

class KaresansuiPlusException(KaresansuiException):
    pass
