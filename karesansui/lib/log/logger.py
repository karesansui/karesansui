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
ロギングプログラム
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

import sys
import logging
import logging.config
from karesansui import KaresansuiException

ready = False
"""<comment-ja>
logging設定が行われているか。
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

class KaresansuiLogError(KaresansuiException):
    """<comment-ja>
    ログ例外クラス
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    pass

def reload_conf(log_conf='/etc/karesansui/log.conf'):
    """<comment-ja>
    loggingの 初期/再 設定を行なう。
    @param log_conf: ログ定義ファイルパス
    @type log_conf: str
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    global ready
    try:
        logging.config.fileConfig(log_conf)
        ready = True
    except:
        ready = False
    
def is_ready():
    """
    <comment-ja>
    ログ出力準備が完了しているか。
    @return bool True(OK) / False(NG)
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    return ready

if __name__ == '__main__':
    pass
