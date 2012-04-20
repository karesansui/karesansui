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

import os
import re
import sys
import time
import email.Parser

from karesansui.lib.dict_op import DictOp
from karesansui.lib.parser.base.null_parser import nullParser as Parser
from karesansui.lib.utils import array_replace
from karesansui.lib.utils import preprint_r


"""
Define Variables for This Parser
"""

class emlParser(Parser):

    _module = "eml"

    def __init__(self):
        self.dop = DictOp()
        self.dop.addconf(self._module,{})

        self.base_parser_name = Parser.__name__

        self.encoding = "UTF-8"
        pass

    def source_file(self):
        try:
            retval = self.get_source_file()
        except:
            retval = []

        return retval

    def _parse_mail(self,mail):
        retval = {}
        try:
            body              = mail.get_payload()
            boundary          = mail.get_boundary()
            charsets          = mail.get_charsets()         # ['iso-8859-1']
            content_charset   = mail.get_content_charset()  # 'iso-8859-1'
            content_maintype  = mail.get_content_maintype() # 'text'
            content_subtype   = mail.get_content_subtype()  # 'plain'
            content_type      = mail.get_content_type()     # 'text/plain'
            default_type      = mail.get_default_type()     # 'text/plain'
            filename          = mail.get_filename()         # ??
            params            = mail.get_params()           # [('text/plain', ''), ('charset', 'iso-8859-1')]
            is_multipart      = mail.is_multipart()         # False
            if type(body) is list:
                new_body = []
                for _mail in body:
                    new_body.append(self._parse_mail(_mail))
                body = new_body
            retval = {}
            retval['body']             = body
            retval['boundary']         = boundary
            retval['charsets']         = charsets
            retval['content_charset']  = content_charset
            retval['content_maintype'] = content_maintype
            retval['content_subtype']  = content_subtype
            retval['content_type']     = content_type
            retval['default_type']     = default_type
            retval['filename']         = filename
            retval['params']           = params
            retval['is_multipart']     = is_multipart
        except:
            pass

        #preprint_r(retval)
        return retval

    def parse(self,file=None,message=None):
        retval = {}
        try:
            if file is not None and os.path.exists(file):
                message = open(file).read()

            mail = email.Parser.Parser().parsestr(message)

            headers  = mail._headers
            msgs     = self._parse_mail(mail)

            if type(msgs['body']) is list:
                rawbody = ""

                if file is not None and os.path.exists(file):
                    f = open(file)
                    line = f.readline()
                    while line:
                        line = f.readline()
                        if line.rstrip() == "":
                            rawbody += line
                            rawbody += ''.join(f.readlines())
                            break
                    f.close
                else:
                    in_body = False
                    for line in message.split("\n"):
                        if line.rstrip() == "":
                            in_body = True
                        if in_body is True:
                            rawbody += line + "\n"

            elif type(msgs['body']) is str:
                rawbody = msgs['body']

            retval["headers"] = headers
            retval["msgs"]    = msgs
            retval["rawbody"] = rawbody

        except:
            pass

        #preprint_r(retval)
        return retval

    def read_conf(self,extra_args=None):
        retval = {}

        self.dop.addconf(self._module,{})

        try:
            self.set_source_file(extra_args["file"])

            for _file in self.source_file():
                if os.path.exists(_file):
                    mail = self.parse(file=_file)

                    headers  = mail['headers']
                    msgs     = mail['msgs']
                    rawbody  = mail['rawbody']

                    self.dop.add(self._module,[_file,'@msgs']   ,msgs)
                    self.dop.add(self._module,[_file,'@headers'],headers)
                    for _header in headers:
                        self.dop.add(self._module,[_file,'header',_header[0]],_header[1])
                    self.dop.add(self._module,[_file,'rawbody'] ,rawbody)

        except:
            pass

        try:
            message = extra_args["message"]

            try:
                message = message.encode(self.encoding)
            except:
                pass

            if message != "" and message is not None:
                mail = self.parse(message=message)

                headers  = mail['headers']
                msgs     = mail['msgs']
                rawbody  = mail['rawbody']

                self.dop.add(self._module,["@message",'@msgs']   ,msgs)
                self.dop.add(self._module,["@message",'@headers'],headers)
                for _header in headers:
                    self.dop.add(self._module,["@message",'header',_header[0]],_header[1])
                self.dop.add(self._module,["@message",'rawbody'] ,rawbody)
        except:
            pass


        return self.dop.getconf(self._module)

    def write_conf(self,conf_arr={},extra_args=None,dryrun=False):
        retval = True

        return retval

"""
"""
if __name__ == '__main__':
    """Testing
    """

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

    parser = emlParser()
    dop = DictOp()
    eml = "/tmp/test2.eml"
    extra_args = {"message":message}
    extra_args = {"file":eml}
    extra_args = {"message":open(eml).read()}
    dop.addconf("dum",parser.read_conf(extra_args=extra_args))
    conf = dop.getconf("dum")
    preprint_r(conf)

