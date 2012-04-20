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
collectdの通知メールを送信する

引数１：宛先メールアドレス
引数２：差出人メールアドレス
引数３：SMTPサーバー名
引数４：SMTPポート名
引数５：本文
引数６：拡張メッセージ
引数７：監視項目名
引数８：ログファイル

"""

DEFAULT_SUBJECT = "[Karesansui notification] '%{watch_name}' threshold exceeded"
DEFAULT_SENDER  = "root@localhost"

import os, sys, re

from karesansui.lib.collectd.utils import append_line
from karesansui.lib.net.mail       import MAIL_LIB, MAIL_LIB_Exception
from karesansui.lib.utils          import preprint_r, ucfirst
from karesansui.lib.parser.eml     import emlParser

from karesansui import __version__, __release__, __app__
AppName = "%s %s" % (ucfirst(__app__),__version__,)

def send_mail(recipient=None, sender=None, server="localhost", port=25, message="", extra_message="", watch_name="", logfile="/dev/null"):
    retval = False

    func_name = sys._getframe(0).f_code.co_name
    append_line(logfile,"[%s] Entering function '%s'." % (func_name,func_name,))

    smtp_server = server.split(":")[0]
    try:
        smtp_port = int(port)
    except:
        smtp_port = 25

    try:
        socket_timeout
    except:
        socket_timeout = 30

    if recipient is not None:

        append_line(logfile,"[%s] Connecting SMTP server" % (func_name,))
        append_line(logfile,"[%s] smtp_server :%s" % (func_name,smtp_server,))
        append_line(logfile,"[%s] smtp_port   :%s" % (func_name,smtp_port,))

        mail = MAIL_LIB(smtp_server,smtp_port)

        if socket_timeout is None:
            socket_timeout = 30
        mail.set_timeout(int(socket_timeout))

        mail.set_verbosity(0)

        if sender is None:
            mail.set_sender(DEFAULT_SENDER)
        else:
            mail.set_sender(sender)

        mail.encoding   = "utf-8"

        mail.set_recipients(recipient.split(","))
        append_line(logfile,"[%s] recipient   :%s" % (func_name,recipient,))

        # デフォルトのヘッダをセット
        headers = {}
        headers['Subject'] = re.sub("\%\{watch_name\}",watch_name,DEFAULT_SUBJECT)

        # カテゴリ用のヘッダとボディを上書きでセット
        rawbody = ""
        try:
            append_line(logfile,"[%s] message   :%s" % (func_name,message,))
            try:
                del headers["Content-Transfer-Encoding"]
                message = message.encode('utf-8')
                message = str(message)
            except:
                pass
            append_line(logfile,"[%s] lang %s" % (func_name,os.environ['LANG']))
            extra_args = {"message":message}
            eml = emlParser().read_conf(extra_args=extra_args)
            parse_ret = preprint_r(eml,return_var=True)
            append_line(logfile,"[%s] parse_ret   :%s" % (func_name,parse_ret,))

            header  = eml['@message']['value']['header']['value']
            rawbody += eml['@message']['value']['rawbody']['value']
            for _k,_v in header.iteritems():
                headers[_k] = _v['value']
        except:
            pass
        try:
            extra_message = extra_message.encode('utf-8')
        except:
            pass
        rawbody += "\n\n" + extra_message

        # Add footer
        rawbody += "\n\n" + "(brought to you by %s)" % AppName

        append_line(logfile,"[%s] rawbody   :%s" % (func_name,rawbody,))

        mail.set_body(rawbody)

        # 一旦メッセージを生成
        mail.create_message()

        #preprint_r(mail.msg._headers)
        for _k,_v in headers.iteritems():
            append_line(logfile,"[%s] Headers %-12s: %s" % (func_name,_k,_v))
            try:
                del mail.msg[_k]
            except:
                pass
            if _k == "Subject":
                try:
                    mail.set_subject(_v.encode('utf_8'))
                except:
                    mail.set_subject(_v)
            else:
                mail.msg[_k] = _v

        try:
            del mail.msg["Content-Transfer-Encoding"]
            mail.msg["Content-Transfer-Encoding"] = "base64"
        except:
            pass

        for _header in mail.msg._headers:
            append_line(logfile,"[%s] Header %-12s: %s" % (func_name,_header[0],_header[1]))
        #sys.exit()

        try:
            mail.send()
            retval = True
        except MAIL_LIB_Exception, msg:
            append_line(logfile,"[%s] Error: %s" % (func_name,str(msg),))
        except Exception:
            append_line(logfile,"[%s] Error: failed to send mail." % (func_name,))

    else:
        append_line(logfile,"[%s] Error: recipient is not set." % (func_name,))

    append_line(logfile,"[%s] Leaving function '%s'." % (func_name,func_name,))
    return retval

if __name__ == '__main__':
    """Testing
    """
    recipient = "taizo@localhost"
    recipient = "root@localhost"
    sender    = None
    server = "localhost"
    logfile = "/dev/stdout"
    watch_name = u'\u30e1\u30e2\u30ea\u4f7f\u7528\u91cf\u3067\u3059'

    message = """Message-ID: <67147291.1.1231874007256.JavaMail.taizo@karesansui-project.info>
Subject: Hello, World!!
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Part_0_22060966.1231404007271"

------=_Part_0_22060966.1231404007271
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: 7bit

E-Mail created by Application
------=_Part_0_22060966.1231404007271
Content-Type: application/pdf; name=HelloWorld_007.pdf
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=HelloWorld_007.pdf
Content-ID: Attachment

JVBERi0xLjMgCiXi48/TIAo3IDAgb2JqCjw8Ci9Db250ZW50cyBbIDggMCBSIF0gCi9QYXJlbnQg

------=_Part_0_22060966.1231404007271--
    """

    message = """Message-ID: <67147291.1.1231874007256.JavaMail.taizo@karesansui-project.info>
Subject: Hello, World!!
MIME-Version: 1.0

Hello World!!
    """
    message = """From: 
To: 
Subject: 
Content-Type: text/plain; charset=ISO-2022-JP
Content-Transfer-Encoding: 7bit

ほげ
Failure

    """

    message = """Subject: [Karesansui Notifier] 危険値を越えました。CPU - %{type_instance}
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

レポート時刻: %{current_time}

ホスト %{hostname} の CPU %{type_instance} が危険値を越えました。

危険値は、%{failure_max} に設定されています。
現在の値は、 %{current_value} です。

    """

    extra_message = u'\u30e1\u30e2\u30ea\u4f7f\u7528\u91cf\u3067\u3059'
    send_mail(recipient=recipient,sender=sender,server=server,message=message,extra_message=extra_message,watch_name=watch_name,logfile=logfile)
    pass

