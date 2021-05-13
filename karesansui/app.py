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

"""
@author: Kei Funagayama <kei@karesansui-project.info>
"""

import sys
import os
import traceback
from os import environ as env
import logging

from .prep import fcgi, built_in, chkconfig, have_privilege

# Initialization
if __name__ == "__main__":
    (config, opts, args) = built_in() # build-in server
    
elif ('FCGI' in env) is True:
    (config, opts, args) = fcgi() # FastCGI server
    
else:
    pass

try:
    import karesansui
except ImportError as e:
    print('[Error] There are not enough libraries. - %s' % ''.join(e.args), file=sys.stderr)
    traceback.format_exc()
    sys.exit(1)
    
if not karesansui.config:
    print('[Error] Failed to load configuration file.', file=sys.stderr)
    sys.exit(1)

if chkconfig(karesansui.config) is False:
    sys.exit(1)

# Check privilege
if have_privilege() is not True:
    from .lib.const import KARESANSUI_GROUP
    print("[Error] Only users who belong to '%s' group are able to run this program." % KARESANSUI_GROUP, file=sys.stderr)
    sys.exit(1)

# Import
import karesansui.lib.log.logger

try:
    import web
    import mako
    import sqlalchemy
    if ('FCGI' in env) is True:
        import flup
    import simplejson
    import libvirt
    # pysilhouette module
    import pysilhouette
except ImportError as e:
    print('[Error] There are not enough libraries. - %s' % ''.join(e.args), file=sys.stderr)
    traceback.format_exc()
    sys.exit(1)

# pysilhouette config read.
from pysilhouette.prep import readconf
karesansui.sheconf = readconf(karesansui.config['pysilhouette.conf.path'])

if karesansui.sheconf is None:
    print('[Error] Failed to load configuration file. (PySilhouette)', file=sys.stderr)
    sys.exit(1)
    
import pysilhouette.prep
if pysilhouette.prep.parse_conf(karesansui.sheconf) is False:
    sys.exit(1)

# URL structure
import karesansui.urls
urls = karesansui.urls.urls


def main():
    """<comment-ja>
    Web Application 起動処理
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    # logging load
    karesansui.lib.log.logger.reload_conf(karesansui.config['application.log.config'])
    if karesansui.lib.log.logger.is_ready() is False:
        raise  karesansui.lib.log.logger.KaresansuiLogError("""Warning!!
        Logging set initial startup failed.
        example : Does the log configuration file exist?
        The present file path : %s
        """ % karesansui.config['application.log.config'])

    logger = logging.getLogger('karesansui.app')
    logger_trace = logging.getLogger('karesansui_trace.app')

    if not os.popen("ps -eo cmd | grep -e ^libvirtd -e ^/usr/sbin/libvirtd").read():
        logger.error('libvirtd not running."/etc/init.d/libvirtd start" Please start.')
        print('[Error] libvirtd not running."/etc/init.d/libvirtd start" Please start.', file=sys.stderr)
        sys.exit(1)
    
    if web.wsgi._is_dev_mode() is True and ('FCGI' in env) is False:
        logger.info('Start Mode [development]')
        app = web.application(urls, globals(), autoreload=True)
        app.internalerror = web.debugerror
        sys.argv = [] # argv clear
    else:
        logger.info('Start Mode [fastcgi]')
        web.config.debug = False
        app = web.application(urls, globals(), autoreload=False)
        #sys.argv = [] # argv clear
        
    # load processor!
    #  - karesansui database!
    app.add_processor(load_sqlalchemy_karesansui)
    logger.info('The load was added. - load_sqlalchemy_karesansui')
    #  - pysilhouette database!
    app.add_processor(load_sqlalchemy_pysilhouette)
    logger.info('The load was added. - load_sqlalchemy_pysilhouette')

    # http://domain/(../..)/hoge
    if karesansui.config['application.url.prefix']:
        mapping = (karesansui.config['application.url.prefix'],  app)
        app = web.subdir_application(mapping)
        
    try:
        if (not opts is None) and opts.shell is True: # shell mode!!
            shell()
        else:
            app.run() # Web Application Start!
    except Exception as e:
        logger_trace.critical(traceback.format_exc())
        print("[ERROR] %s" % str(e.args), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1

# webpy - processor
def load_sqlalchemy_karesansui(handler):
    """<comment-ja>
    リクエストスコープ単位にKaresansuiデータベースのセッションを割り当てる。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    import karesansui.db
    web.ctx.orm = karesansui.db.get_session()
    
    logger = logging.getLogger("karesansui.processor.karesansui")

    logger.debug('Karesansui database session scope [start] - %s' % web.ctx.orm)
    try:
        ret = handler()
        web.ctx.orm.commit()
        logger.debug('Karesansui database session scope [commit] - %s' % web.ctx.orm)
        return ret 
    except web.HTTPError:
        if web.ctx.status[:1] in ['2', '3']:
            web.ctx.orm.commit()
            logger.debug('Karesansui database session scope [commit] : HTTP Status=%s - %s' % (web.ctx.status, web.ctx.orm))
            raise
        else:
            web.ctx.orm.rollback()
            logger.debug('Karesansui database session scope [rollback] : HTTP Status=%s - %s' % (web.ctx.orm, web.ctx.status))
            raise
    except:
        web.ctx.orm.rollback()
        logger.debug('Karesansui database session scope [rollback] - %s' % web.ctx.orm)
        raise

def load_twophase_sqlalchemy(handler):
    """<comment-ja>
    KaresansuiとPysilhouetteデータベースの2フェーズセッションをWeb Applicationに割り当てる。
    sqiteが2フェーズに対応していないのでVersion1.xでは未対応。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    #: <= 2.0
    # sqlite not supported.
    Session = sqlalchemy.orm.sessionmaker(twophase=True)
    Session.configure(binds={karesansui.db.get_metadata():karesansui.db.get_engine(),
                             karesansui.db._2pysilhouette.get_metadata():karesansui.db._2pysilhouette.get_engine(),
                             })
    session = Session()

def load_sqlalchemy_pysilhouette(handler):
    """<comment-ja>
    リクエストスコープ単位にPysilhouetteデータベースのセッションを割り当てる。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    import karesansui.db._2pysilhouette
    from web.utils import Storage
    web.ctx.pysilhouette = Storage()
    web.ctx.pysilhouette.orm = karesansui.db._2pysilhouette.get_session()
    
    logger = logging.getLogger("karesansui.processor.pysilhouette")
    
    try:
        ret = handler()
        web.ctx.pysilhouette.orm.commit()
        logger.debug('Pysilhouette database session scope [commit] - %s' % web.ctx.orm)
        return ret 
    except web.HTTPError:
        if web.ctx.status[:1] in ['2', '3']:
            web.ctx.pysilhouette.orm.commit()
            logger.debug('Pysilhouette database session scope [commit] : HTTP Status=%s - %s' % (web.ctx.status, web.ctx.orm))
            raise
        else:
            web.ctx.pysilhouette.orm.rollback()
            logger.debug('Pysilhouette database session scope [rollback] : HTTP Status=%s - %s' % (web.ctx.orm, web.ctx.status))
            raise
    except:
        web.ctx.pysilhouette.orm.rollback()
        logger.debug('Karesansui database session scope [commit] - %s' % web.ctx.orm)
        raise


def shell():
    """<comment-ja>
    IPythonを利用したKaresansui コマンドライン
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    try:
        from IPython.Shell import IPShellEmbed
    except ImportError as e:
        print('[Error] Shell function requires IPython. - %s' % ''.join(e.args), file=sys.stderr)
        traceback.format_exc()
        sys.exit(1)

    # karesansui database
    import karesansui.db
    kss_engine = karesansui.db.get_engine()
    kss_metadata = karesansui.db.get_metadata()
    kss_session = karesansui.db.get_session()
    # pysilhouette
    import karesansui.db._2pysilhouette 
    pyshe_engine = karesansui.db._2pysilhouette.get_engine()
    pyshe_metadata = karesansui.db._2pysilhouette.get_metadata()
    pyshe_session = karesansui.db._2pysilhouette.get_session()
    
    ipshell = IPShellEmbed()
    return ipshell()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
