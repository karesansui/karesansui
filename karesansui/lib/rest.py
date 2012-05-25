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
Rest(Gadget)全体を司る
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

from datetime import datetime
from base64 import b64decode
from gettext import translation as translation
import logging
import traceback
import os

import web
from web.utils import Storage
from web.contrib.template import render_mako

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import karesansui
from karesansui.lib.utils import is_int, is_param, karesansui_database_exists
from karesansui.db.access.user import login as dba_login
from karesansui.db.access.machine import is_findbyhost1, is_findbyguest1
from karesansui.lib.const import LOGOUT_FILE_PREFIX, DEFAULT_LANGS

BASIC_REALM = 'KARESANSUI_AUTHORIZE'
"""<comment-ja>
Basic Authの Basic realm 名
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

GET='GET'
POST='POST'
PUT='PUT'
DELETE='DELETE'

OVERLOAD_METHOD='_method'
"""<comment-ja>
オーバーロードメソッドのinput名
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

ERROR_MEDIA = ['html', 'json', 'part', 'input']
"""<comment-ja>
対応しているErrorページのメディアタイプ
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

DEFAULT_MEDIA = 'html'
"""<comment-ja>
デフォルトのメディアタイプ
</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

OUTPUT_TYPE_NORMAL = 0
OUTPUT_TYPE_FILE = 1
OUTPUT_TYPE_STREAM = 2
"""<comment-ja>

</comment-ja>
<comment-en>
TODO: English Comment
</comment-en>
"""

class Rest:
    """<comment-ja>
    全てのRest基底クラス
    Restを使用する場合は本クラスを継承してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    def __init__(self):
        """<comment-ja>
        リクエスト単位で初期化する処理を行います。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        self.__method__ = GET
        """<comment-ja>
        HTTP Method
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
    
        self.view = Storage()
        """<comment-ja>
        テンプレートへ渡したい値をセットする変数
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        self.input = Storage()
        """<comment-ja>
        リクエスト情報、各種設定値が設定されている変数
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """

        self.__template__ = Storage()

        self.download = Storage()

        # self setting
        self.logger = logging.getLogger('karesansui.rest')
        self.logger_trace = logging.getLogger('karesansui_trace.rest')
        self.orm = web.ctx.orm
        self.pysilhouette = web.ctx.pysilhouette
        self.view.ctx = web.ctx
        self.view.alert = []
        self.me = None
        self.languages = [ unicode(karesansui.config['application.default.locale']), ]
        self._ = mako_translation(languages=self.languages)
        
        # templates
        self.__template__.dir = self.__class__.__name__.lower()
        self.__template__.file = self.__class__.__name__.lower()
        self.__template__.media = DEFAULT_MEDIA

        # download
        self.download.file = None
        self.download.stream = None
        self.download.type = OUTPUT_TYPE_NORMAL
        self.download.once = False

    def _pre(self, *param, **params):
        """<comment-ja>
        HTTP Method別処理を実行する前の処理を行います。
          1. メディアタイプの設定
          2. Content-Typeの設定
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        multi = {}
        for x in web.input(_unicode=False).keys():
            if x.startswith('multi') is True:
                multi[x] = {}
        self.input = web.input(**multi)
        
        try:
            if param:
                resource = web.websafe(param[len(param)-1])
                self.__template__.media = resource[resource.rindex('.')+1:]
                
        except (IndexError, ValueError), ve:
            self.__template__.media = DEFAULT_MEDIA
            self.logger.debug(
                '%s - The media-type has not been specified, or that violate the format, so use a standard format. :Media=%s' \
                % (' '.join(ve.args), self.__template__.media))

        if self.input.has_key('mode') and self.input.mode == 'input':
            self.__template__.media = self.input.mode

    def _post(self, f):
        """<comment-ja>
        HTTP Method別処理を実行した後の処理を行います。
          1. HTTP Responseコード 4xx or 5xx についての処理
          2. テンプレート処理
          3. HTTP Headerをセット
        @param f: 実行結果
        @type f: bool or web.HTTPError
        @return: HTTP Response
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        try: # default view set.
            self.view.me = self.me
            if self.is_standalone() is True:
                self.view.standalone = self.input.standalone
        except AttributeError:
            pass

        # Content-Type
        # TODO
        # "Resource interpreted as script but transferred with MIME type text/plain."
        #if self.__template__.media == 'part':
        #    web.header('Content-Type', 'text/html; charset=utf-8', True)
        #elif self.__template__.media == 'input':
        #    web.header('Content-Type', 'text/html; charset=utf-8', True)
        #elif self.__template__.media == 'html':
        #    web.header('Content-Type', 'text/html; charset=utf-8', True)
        #elif self.__template__.media == 'json':
        #    web.header('Content-Type', 'application/json; charset=utf-8', True)
        #elif self.__template__.media == 'xml':`
        #    web.header('Content-Type', 'text/xml; charset=utf-8', True)
        #elif self.__template__.media == 'gif':
        #    web.header('Content-Type', 'Content-type: image/gif', True)
        #elif self.__template__.media == 'png':
        #    web.header('Content-Type', 'Content-type: image/png', True)
        #elif self.__template__.media == 'jpg':
        #    web.header('Content-Type', 'Content-type: image/jpeg', True)
        #elif self.__template__.media == 'jpeg':
        #    web.header('Content-Type', 'Content-type: image/jpeg', True)
        #elif self.__template__.media == 'ico':
        #    web.header('Content-Type', 'Content-type: image/x-icon', True)
        #elif self.__template__.media == 'css':
        #    web.header('Content-Type', 'Content-type: text/css; charset=utf-8', True)
        #elif self.__template__.media == 'js':
        #    web.header('Content-Type', 'Content-type: text/javascript; charset=utf-8', True)
        #elif self.__template__.media == 'jar':
        #    web.header('Content-Type', 'Content-type: application/java-archiver', True)
        #else:
        #    web.header('Content-Type', 'text/plain; charset=utf-8', True)

        # HTTP Header - No Cache
        now = datetime.now()
        web.lastmodified(now)
        web.httpdate(now)
        # TODO
        #web.expire(0)
        #web.header('Expires', web.httpdate(datetime(1970,1,1)))
        #web.header('Last-Modified',  web.httpdate(datetime(1970,1,1)))
        #web.header('ETag', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        web.header('Cache-Control', 'no-cache,private')
        web.header('Pragma', 'no-cache')

        ##
        if self.download.type == OUTPUT_TYPE_NORMAL: # Nomal
            if self.me is None:
                self.view.USER_DATE_FORMAT = DEFAULT_LANGS[self.languages[0]]['DATE_FORMAT']
            else:
                self.view.USER_DATE_FORMAT = DEFAULT_LANGS[self.me.languages]['DATE_FORMAT']

            if isinstance(f, web.HTTPError) is True:
                self.logger.info('HTTP Response - %s Headers-->%s' % (f.__class__.__name__, web.ctx.headers))
                raise f

            if f is True:
                path = '%s/%s.%s' % (self.__template__.dir, self.__template__.file, self.__template__.media,)
            else:
                #if self.__template__.media in ERROR_MEDIA:
                #    path = 'error/error.%s' % self.__template__.media
                #else:
                #    path = 'error/error.%s' % DEFAULT_MEDIA
                self.logger.info('"gadget" execution error - %s' % str(self.__class__))
                raise web.internalerror("Execution errors")

            self.logger.debug('lang=%s %s : template=%s' \
                              % (','.join(self.languages), str(self), path))

            try:
                _r = mako_render(self._, path,
                                 title=self._('Karesansui'), view=self.view)
                return _r
            except:
                if web.wsgi._is_dev_mode() is True and os.environ.has_key('FCGI') is False:
                    return exceptions.html_error_template().render(full=True)
                else:
                    self.logger.error('"mako render" execution error - path=%s' % path)
                    self.logger_trace.error(traceback.format_exc())
                    raise web.internalerror("Execution errors")

        elif self.download.type == OUTPUT_TYPE_FILE: # file download
            if self.download.file is None or os.path.isfile(self.download.file) is False:
                self.logger.error('Could not find files to download. - path=%s' % self.download.file)
                return web.internalerror()
            web.header('Content-Type', 'Content-type: image/png', True)
            fp = open(self.download.file , "rb")
            try:
                _r = fp.read()
            finally:
                fp.close()

            if self.download.once is True and os.path.isfile(self.download.file) is True:
                os.unlink(self.download.file)

            return _r

        elif self.download.type == OUTPUT_TYPE_STREAM: # io stream download
            if self.download.stream is None:
                self.logger.error("Data stream has not been set.")
            return self.download.stream

        else:
            self.logger.error('Was specified assuming no output type. - type=%d' % self.download.type)
            raise web.internalerror()

    def POST(self, *param, **params):
        """<comment-ja>
        Method POSTの処理を行います。
          - オーバーロードPOSTに対応しています。
            - リクエストの中に _method を設定することで動作します。(POST,PUT,DELETE)
            - 例) <input type='hidden' name='_method' value='POST' />
          - 各処理は継承先で _POST メソッドを作成し、そこに記述してください。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        try:
            if web.input(_unicode=False).has_key(OVERLOAD_METHOD):
                self.__method__ = web.input(_unicode=False)[OVERLOAD_METHOD].upper()
                if self.__method__ == PUT:
                    self.__method__ = PUT
                    self.logger.debug("OVERLOAD - POST -> PUT")
                    return self.__method_call(*param, **params)
                elif self.__method__ == DELETE:
                    self.__method__ = DELETE
                    self.logger.debug("OVERLOAD - POST -> DELETE")
                    return self.__method_call(*param, **params)
                elif self.__method__ == GET:
                    self.__method__ = GET
                    self.logger.debug("OVERLOAD - POST -> GET")
                    return self.__method_call(*param, **params)

            # POST Method
            self.__method__ = POST    
            self._pre(*param, **params)
            _r = self.__method_call(prefix='_', *param, **params)
            return self._post(_r)
        except web.HTTPError, e:
            raise
        except:
            self.logger_trace.error(traceback.format_exc())
            #return web.internalerror()
            raise

    def GET(self, *param, **params):
        """<comment-ja>
        Method GETの処理を行います。
          - 各処理は継承先で _GET メソッドを作成し、そこに記述してください。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        try:
            self._pre(*param, **params)
            _r = self.__method_call(prefix='_', *param, **params)
            return self._post(_r)
        except web.HTTPError, e:
            raise
        except:
            self.logger_trace.error(traceback.format_exc())
            #return web.internalerror()
            raise

    def PUT(self, *param, **params):
        """<comment-ja>
        Method PUTの処理を行います。
          - 各処理は継承先で _PUT メソッドを作成し、そこに記述してください。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        try:
            self.__method__ = PUT
            self._pre(*param, **params)
            _r = self.__method_call(prefix='_', *param, **params)
            return self._post(_r)
        except web.HTTPError, e:
            raise
        except:
            self.logger_trace.error(traceback.format_exc())
            #return web.internalerror()
            raise
    
    def DELETE(self, *param, **params):
        """<comment-ja>
        Method DELETEの処理を行います。
          - 各処理は継承先で _DELETE メソッドを作成し、そこに記述してください。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        try:
            self.__method__ = DELETE
            self._pre(*param, **params)
            _r = self.__method_call(prefix='_', *param, **params)
            return self._post(_r)
        except web.HTTPError, e:
            raise
        except:
            self.logger_trace.error(traceback.format_exc())
            #return web.internalerror()
            raise

    def __method_call(self, *param, **params):
        """<comment-ja>
        各Methodを動的に呼び出します。
          - paramsに prefixを指定することができます。
            - 例) prefix='_' or prefix=''
          - 存在しないMethodの場合は web.nomethod() を返却します。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        if params.has_key('prefix'):
            prefix = params.pop('prefix')
        else:
            prefix = ''

        try:
            if hasattr(self, prefix + self.__method__) is True:
                method = getattr(self, prefix + self.__method__)
                return method(*param, **params)
            else:
                self.logger.debug('%s : Method=%s - Not Method' %
                                  (str(self), self.__method__))
                self._ = mako_translation(languages=self.languages)
                return web.nomethod()
        except:
            self.logger.error("__method_call() error - prefix=%s languages=%s" \
                              % (str(prefix), str(self.languages)))
            raise
    ### --  util
    def is_mode_input(self):
        """<comment-ja>
        URLパラメタにmode=inputが存在するかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.__template__.media == 'input':
            return True
        else:
            return False

    def is_part(self):
        """<comment-ja>
        メディアがpartかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.__template__.media == 'part':
            return True
        else:
            return False

    def is_json(self):
        """<comment-ja>
        メディアがjsonかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.__template__.media == 'json':
            return True
        else:
            return False

    def is_html(self):
        """<comment-ja>
        メディアがhtmlかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.__template__.media == 'html':
            return True
        else:
            return False

    def is_xml(self):
        """<comment-ja>
        メディアがxmlかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.__template__.media == 'xml':
            return True
        else:
            return False

    def is_standalone(self):
        """<comment-ja>
        URLパラメタにstandalone=1が存在するかどうか。
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if self.is_mode_input() is True or self.is_part() is True and is_param(self.input, "standalone") and self.input.standalone == "1":
            return True
        else:
            return False

    def chk_hostby1(self, param):
        """<comment-ja>
        param[0] のホストIDの型とデータベースに存在しているかチェックする。

        @param param: rest#param
        @type param: dict
        @return: check ok : int(param[0]) || check ng : None
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if is_int(param[0]) is True:
            if is_findbyhost1(self.orm, param[0]) == 1:
                return int(param[0])
            else:
                return None
        else:
            return None

    def chk_guestby1(self, param):
        """<comment-ja>
        param[1] のゲストIDの型とデータベースに存在しているかチェックする。ゲストIDの親ホストIDもチェックする。

        @param param: rest#param
        @type param: dict
        @return: check ok : int(param[0]), int(param[1]) : check ng : None, None
        @rtype: bool
        </comment-ja>
        <comment-en>
        English Comment
        </comment-en>
        """
        if is_int(param[1]) is True:
            if is_findbyguest1(self.orm, param[1]) == 1:
                if not (self.chk_hostby1(param) is None):
                    return int(param[0]), int(param[1])
                else:
                    return None, None
            else:
                return None, None
        else:
            return None, None

# -- HTTP Response Code
class Unauthorized(web.HTTPError):
    """<comment-ja>
    401 Unauthorized errorクラス
    呼出は直接ではなく、karesansui.lib.rest.unauthorized を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, data='unauthorized'):
        if isinstance(data, list):
            data = "\n".join(data)

        global BASIC_REALM
        status = "401 Unauthorized"
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'WWW-Authenticate': 'Basic realm="%s"' % BASIC_REALM
        }
        web.HTTPError.__init__(self, status, headers, data)
        
web.unauthorized = Unauthorized

class Conflict(web.HTTPError):
    """<comment-ja>
    409 Conflict errorクラス
    呼出は直接ではなく、karesansui.lib.rest.conflict を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, url, data='conflict'):
        if isinstance(data, list):
            data = "\n".join(data)

        status = "409 Conflict"
        headers = { 
            'Content-Type': 'text/html; charset=utf-8',
        }
        headers['Location'] = url
        web.HTTPError.__init__(self, status, headers, data)

web.conflict = Conflict

class Created(web.HTTPError):
    """<comment-ja>
    201 Created クラス
    呼出は直接ではなく、karesansui.lib.rest.created を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, url, data='created'):
        if isinstance(data, list):
            data = "\n".join(data)

        status = "201 Created"
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Location': url
        }
        web.HTTPError.__init__(self, status, headers, data)

web.created = Created

class Accepted(web.HTTPError):
    """<comment-ja>
    202 Accepted クラス
    呼出は直接ではなく、web.accepted を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, data='accepted', url=None):
        if isinstance(data, list):
            data = "\n".join(data)

        status = "202 Accepted"
        headers = {
                'Content-Type': 'text/html; charset=utf-8',
        }
        if url:
            headers['Location'] = url
        web.HTTPError.__init__(self, status, headers, data)

web.accepted = Accepted

class NoContent(web.HTTPError):
    """<comment-ja>
    204 No Content クラス
    呼出は直接ではなく、web.nocontent を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self):
        status = "204 No Content"
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
        }
        web.HTTPError.__init__(self, status, headers)

web.nocontent = NoContent

#class RequestTimeout(web.HTTPError):
#    """<comment-ja>
#    408 Request Timeout クラス
#    呼出は直接ではなく、web.requesttimeout を利用してください。
#    </comment-ja>
#    <comment-en>
#    TODO: English Comment
#    </comment-en>
#    """
#    def __init__(self):
#        status = "408 Request Timeout"
#        web.HTTPError.__init__(self, status)
#
#web.requesttimeout = RequestTimeout

def NotFound(data = None):
    """<comment-ja>
    404 Not Found メソッド
    呼出は直接ではなく、web.notfound を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if isinstance(data, list):
        data = "\n".join(data)

    return web.NotFound(data)

web.notfound = NotFound

def InternalError(data = None):
    """<comment-ja>
    500 InternalError メソッド
    呼出は直接ではなく、web.internalerror を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if isinstance(data, list):
        data = "\n".join(data)

    return web.InternalError(data)

web.internalerror = InternalError

class BadRequest(web.HTTPError):
    """<comment-ja>
    400 Bad Request クラス
    呼出は直接ではなく、web.badrequest を利用してください。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    def __init__(self, data="bad request"):
        if isinstance(data, list):
            data = "\n".join(data)

        status = "400 Bad Request"
        headers = {'Content-Type': 'text/html'}
        web.HTTPError.__init__(self, status, headers, data)

web.badrequest = BadRequest

# -- Bacis Auth Decorator
def auth(func):
    """<comment-ja>
    Basic認証を行います。
      - 認証方式はDB認証
        - 認証に失敗した場合は、401 Unauthorizedなります。
        - 認証に成功すると、呼出元のクラスに me,languages,_ がセットされます。
          - me: ログインユーザ情報が設定されます。(karesansui.db.user.User)
          - languages: locale情報が設定されます。(左から評価されます)
          - _: 国際化メソッドが設定されます。( 使い方 : _('hoge') )
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """


    def wrapper(self, *args, **kwargs):

        if web.ctx.path[0:6] == '/data/':
            self._ = mako_translation(languages=[ unicode(karesansui.config['application.default.locale']), ])
            return func(self, *args, **kwargs)

        if karesansui_database_exists() is False:
            return web.tempredirect(web.ctx.path + "init", absolute=False)

        if web.ctx.env.has_key('HTTP_AUTHORIZATION'):
            (user, email) = login()

            if user:
                self.me = user

                # Logout
                fname = '%s%s' % (LOGOUT_FILE_PREFIX, self.me.email,)
                if os.access(fname, os.F_OK):
                    os.unlink(fname)
                    return web.unauthorized()

                # Login: Success
                if user.languages in self.languages:
                    x = self.languages.index(user.languages)
                    self.languages.pop(x)
                    
                self.languages.insert(0, user.languages)
                self.logger.info('user_id=%s,lang=%s : Method=%s - Basic Authentication=Success' %
                                  (self.me.id, ','.join(self.languages), self.__method__))
                
                # __init__#self._ update!!
                self._ = mako_translation(languages=self.languages)
                return func(self, *args, **kwargs)
            else:
                 # Login: Failure
                self.logger.info('user=%s : Method=%s - Basic Authentication=Failure' %
                                  (email, self.__method__))
                return web.unauthorized()
        else:
            # Login: Anonymous
            self.logger.info('user=anonymous : Method=%s - Basic Authentication=Anonymous' %
                              (self.__method__))
            return web.unauthorized()
        
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

# -- Basic Auth
def login():
    """<comment-ja>
    ログインチェックを行います。
    @return: ログインユーザ情報
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    _http_auth = web.ctx.env['HTTP_AUTHORIZATION'].strip()
    if _http_auth[:5] == 'Basic':
        email, password = b64decode(_http_auth[6:].strip()).split(':')
        session = web.ctx.orm
        user = dba_login(session, unicode(email), unicode(password))
        return (user, email)

# -- Template Engine
def mako_render(_, templatename, **kwargs):
    """<comment-ja>
    テンプレート実行結果の出力
    @param _: 国際化メソッド
    @type var: gettext.GNUTranslations
    @param templatename: テンプレート名
    @type templatename: str
    @param kwargs:
    @type kwargs:    
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    logger = logging.getLogger('karesansui.rest.mako')
    if templatename.startswith('static/') is True:
        directories = [karesansui.dirname, 'static', templatename[7:]]
        filepath = '/'.join(directories)
        logger.debug(filepath)

        fp = open(filepath, "r")
        try:
            return fp.read()
        finally:
            fp.close()

    else:
        directories = [karesansui.dirname, 'templates']
        if karesansui.config.has_key('application.template.theme'):
            directories.append(karesansui.config['application.template.theme'])
        else:
            directories.append('default')

    tl = TemplateLookup(directories='/'.join(directories),
                        input_encoding='utf-8',
                        output_encoding='utf-8',
                        default_filters=['decode.utf8'],
                        encoding_errors='replace')
    
    try:
        t = tl.get_template(templatename)
    except exceptions.TopLevelLookupException, tlle:
        logger.error('We could not find the template directory. - %s/%s'
                     % ('/'.join(directories), templatename))
        return web.notfound()
        
    logger.info('Template file path=%s' % t.filename)
    kwargs['_'] = _ # gettex
    
    view = {}
    if kwargs.has_key('view'):
        for x in kwargs['view'].keys():
            view[x] = kwargs['view'][x]
        kwargs.pop('view')
    kwargs.update(view)
    return t.render(**kwargs)

def mako_translation(languages, domain='messages', localedir='locale'):
    """<comment-ja>
    国際化処理
    @param languages: 対象言語
    @type languages: list
    @param domain: ドメイン名
    @type domain: str
    @param localedir: localeディレクトリ
    @type localedir: str
    @return: gettext.GNUTranslations
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    localedir = '/'.join([karesansui.dirname, localedir])
    return translation(domain, localedir, tuple(languages)).ugettext 

if __name__ == "__main__":
    pass
