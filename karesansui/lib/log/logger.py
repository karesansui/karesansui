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
