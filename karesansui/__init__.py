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
__release__ = '0'
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
