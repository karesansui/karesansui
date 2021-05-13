#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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
import os.path
from os import environ as env
import traceback
from optparse import OptionParser, OptionValueError

try:
    import karesansui
except ImportError:
    from . import __init__ as karesansui

from karesansui.lib.utils import is_uuid, is_int
from .lib.file.k2v import K2V 

usage = "%prog [options]"
version = 'karesansui %s' % karesansui.__version__

def getopts():
    """<comment-ja>
    コマンドラインオプションの解析
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    optp = OptionParser(usage=usage, version=version)
    optp.add_option('-c', '--config', dest='cf', help='Configuration file of application')
    optp.add_option('-s', '--shell', dest='shell', action="store_true", help='Start at the terminal.(IPython)')
    return optp.parse_args()

def chkopts(opts):
    """<comment-ja>
    コマンドラインオプションチェック
    @param opts: コマンドラインオプション
    @type opts: OptionParser#parse_args()
    @rtype: bool
    @return: チェック結果
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if not opts.cf:
        print('%s: --config is required.' % karesansui.__app__, file=sys.stderr)
        return True

    if os.path.isfile(opts.cf) is False:
        print('-c or --config file is specified in the option does not exist.', file=sys.stderr)
        return True

def chkconfig(config):
    """<comment-ja>
    Karesansui設定ファイル情報をチェックします。
    @param config: 設定ファイル情報
    @type config: dict
    @rtype: bool
    @return: チェック結果
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    check = True

    # application.log.config
    if check and ("application.log.config" in config) is False:
        print('Configuration information is missing. - application.log.config', file=sys.stderr)
        check = False

    if check and os.path.isfile(config["application.log.config"]) is False:
        print('There is a mistake in the configuration information. - application.log.config=%s' % config["application.log.config"], file=sys.stderr)
        check = False

    # application.tmp.dir
    if check and ("application.tmp.dir" in config) is False:
        print('Configuration information is missing. - application.tmp.dir', file=sys.stderr)
        check = False

    if check and os.path.isdir(config["application.tmp.dir"]) is False:
        print('There is a mistake in the configuration information. - application.tmp.dir=%s' % config["application.tmp.dir"], file=sys.stderr)
        check = False

    if check and os.access(config["application.tmp.dir"], os.R_OK | os.W_OK) is False:
        print('Not set the appropriate permissions to that directory. - application.tmp.dir=%s' % config["application.tmp.dir"], file=sys.stderr)
        check = False

    # application.bin.dir
    if check and ("application.bin.dir" in config) is False:
        print('Configuration information is missing. - application.bin.dir', file=sys.stderr)
        check = False

    if check and os.path.isdir(config["application.bin.dir"]) is False:
        print('There is a mistake in the configuration information. - application.bin.dir=%s' % config["application.bin.dir"], file=sys.stderr)
        check = False

    if check and os.access(config["application.bin.dir"], os.R_OK) is False:
        print('Not set the appropriate permissions to that directory. - application.bin.dir=%s' % config["application.bin.dir"], file=sys.stderr)
        check = False

    # pysilhouette.conf.path
    if check and ("pysilhouette.conf.path" in config) is False:
        print('Configuration information is missing. - pysilhouette.conf.path', file=sys.stderr)
        check = False
        
    if check and os.path.isfile(config["pysilhouette.conf.path"]) is False:
        print('There is a mistake in the configuration information. - pysilhouette.conf.path=%s' % config["pysilhouette.conf.path"], file=sys.stderr)
        check = False

    if check and os.access(config["pysilhouette.conf.path"], os.R_OK) is False:
        print('Not set the appropriate permissions to that file. - pysilhouette.conf.path=%s' % config["pysilhouette.conf.path"], file=sys.stderr)
        check = False

    # application.uniqkey
    if check and ("application.uniqkey" in config) is False:
        print('Configuration information is missing. - application.uniqkey', file=sys.stderr)
        check = False

    if check and is_uuid(config["application.uniqkey"]) is False:
        print('UUID format is not set. - application.uniqkey', file=sys.stderr)
        check = False

    # database.pool.status
    if check and ("database.pool.status" in config) is False:
        print('Configuration information is missing. - database.pool.status', file=sys.stderr)
        check = False

    if check and (config["database.pool.status"] in ("0","1")) is False:
        print('The mistake is found in the set value. Please set 0 or 1. - database.pool.status', file=sys.stderr)
        check = False

    if check and config["database.pool.status"] == "1":
        # database.pool.max.overflow
        if check and ("database.pool.max.overflow" in config) is False:
            print('Configuration information is missing. - database.pool.max.overflow', file=sys.stderr)
            check = False

        # database.pool.size
        if check and ("database.pool.size" in config) is False:
            print('Configuration information is missing. - database.pool.size', file=sys.stderr)
            check = False

        # int
        if check and is_int(config["database.pool.max.overflow"]) is False:
            print('Please set it by the numerical value. - database.pool.max.overflow', file=sys.stderr)
            check = False

        if check and is_int(config["database.pool.size"]) is False:
            print('Please set it by the numerical value. - database.pool.size', file=sys.stderr)
            check = False

        if check and int(config["database.pool.size"]) <= 0:
            print('Please set values that are larger than 0. - database.pool.size', file=sys.stderr)
            check = False

        # Comparison
        if check and int(config["database.pool.max.overflow"]) < int(config["database.pool.size"]):
            print('Please set "database.pool.max.overflow" to a value that is larger than "database.pool.size".', file=sys.stderr)
            check = False

    return check

def built_in():
    """<comment-ja>
    built-in Web Server 起動処理
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    # Built-in Web server
    conf = ''
    (opts, args) = getopts()
    if opts.cf: # option
        if chkopts(opts): sys.exit(1)
        conf = opts.cf
        env['KARESANSUI_CONF'] = conf
    elif env.get('KARESANSUI_CONF'): # envrion
        conf = env.get('KARESANSUI_CONF')
    else: #error
        print('[built_in] Please specify the configuration file. - Please set the environment variable that "KARESANSUI_CONF". Otherwise, please set the command option that "-c or --config".', file=sys.stderr)
        sys.exit(1)

    config = None
    if conf: # read file
        conf = os.path.abspath(conf)
        _k2v = K2V(conf)
        config = _k2v.read()
    else: # error
        print('[built_in] Please specify the configuration file. - Environment variables or command-option', file=sys.stderr)
        sys.exit(1)

#    if env.has_key('SEARCH_PATH'):
#        for y in [x.strip() for x in env.get('SEARCH_PATH').split(',') if x]:
#            if (y in sys.path) is False: sys.path.insert(0, y)

    if config and 'application.search.path' in config:
        for y in [x.strip() for x in config['application.search.path'].split(',') if x]:
            if (y in sys.path) is False: sys.path.insert(0, y)

    import karesansui
    karesansui.config = config
    return config, opts, args

def fcgi():
    """<comment-ja>
    外部Web Server(FastCGI) 起動処理
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    # WebServer(fcgi)
    conf = ''
    if env.get('KARESANSUI_CONF'): # envrion
        conf = env.get('KARESANSUI_CONF')
    else: #error
        print('[fcgi] Please specify the configuration file. - Please set the environment variable that "KARESANSUI_CONF".', file=sys.stderr)
        sys.exit(1)

    config = None
    if conf: # read file
        _k2v = K2V(conf)
        config = _k2v.read()

    try:
        import flup
    except ImportError as e:
        print('[Error] There are not enough libraries.(fcgi) - %s' % ''.join(e.args), file=sys.stderr)
        traceback.format_exc()
        sys.exit(1)


    if config and 'application.search.path' in config:
        for y in [x.strip() for x in config['application.search.path'].split(',') if x]:
            if (y in sys.path) is False: sys.path.insert(0, y)

#    if env.has_key('SEARCH_PATH'):
#        for y in [x.strip() for x in env.get('SEARCH_PATH').split(',') if x]:
#            if (y in sys.path) is False: sys.path.insert(0, y)

    import karesansui
    karesansui.config = config
    return config , None, None

def create__cmd__(config, conf):
    """<comment-ja>
    Karesansuiで使用する実行コマンドで使用する__cmd__.pyを生成する。
    生成場所: 'application.bin.dir'
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    # create __cmd__.py file
    from .lib.file.configfile import ConfigFile
    from .lib.utils import r_chgrp
    from .lib.const import KARESANSUI_GROUP

    command_py = "%s/__cmd__.py" % config['application.bin.dir']
    ConfigFile(command_py).write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

karesansui_conf = '%s'
search_path = '%s'
pysilhouette_conf = '%s'

""" % (conf, config['application.search.path'], config['pysilhouette.conf.path']))
    
    if os.path.exists(command_py) and os.getuid() == 0:
        r_chgrp(command_py,KARESANSUI_GROUP)

def have_privilege(msg=True):
    """<comment-ja>
    実行可能ユーザーかどうかの判定
    </comment-ja>
    <comment-en>
    Return True if the current process should be able to run karesansui.
    </comment-en>
    """
    import os
    import pwd, grp
    from .lib.const import KARESANSUI_USER, KARESANSUI_GROUP

    try:
        ok_gr = grp.getgrnam(KARESANSUI_GROUP)[3]
        ok_gr.append(grp.getgrgid(pwd.getpwnam(KARESANSUI_USER)[3])[0])
    except:
        ok_gr = []

    ret = (grp.getgrgid(os.getgid())[0] in ok_gr)
    if ret is False and msg is True:
        print("""
# chgrp -R %s %s
# chmod -R g+w %s
# chgrp -R %s %s
# chmod -R g+w %s
Or check permission of the following directories.
* log file directory
* configuration file directory
""" % (KARESANSUI_GROUP,karesansui.config['application.bin.dir'],karesansui.config['application.bin.dir'], KARESANSUI_GROUP,os.path.dirname(__file__),os.path.dirname(__file__),
), file=sys.stderr)
    return ret

if __name__ == '__main__':
    pass
