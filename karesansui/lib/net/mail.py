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
import sys
import time
import glob
import re
import socket
import traceback

import smtplib
from email import message_from_string
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Message import Message
from email.Charset import Charset, QP
from email.Header import Header
from email.Utils import formatdate
from mimetypes import guess_type

default_timeout = 30

class MAIL_LIB_Exception(Exception):
    """Command execution error.
    """
    pass

class MAIL_LIB:

    def __init__(self, smtp_server="localhost", smtp_port=25):

        self.verbose  = False
        self.timeout  = None

        self.smtp_server = smtp_server
        self.smtp_port   = int(smtp_port)

        self.encoding   = "utf-8"
        self.sender     = None
        self.recipients = []
        self.subject    = ""
        self.body       = ""
        self.attach     = None

        self.tls = False
        if self.smtp_port == 587:
            self.tls = True

        self.auth_user   = None
        self.auth_passwd = None

    def set_verbosity(self,flag=0):
        if flag == 0:
            self.verbose = False
        else:
            self.verbose = True

    def set_timeout(self,seconds=30):
        self.timeout = seconds

    def set_sender(self,sender):
        self.sender = sender

    def set_recipients(self,recipients):
        if type(recipients) is str:
            self.recipients = [recipients,]
        else:
            self.recipients = recipients

    def add_recipient(self,recipient):
        if type(recipient) is str:
            self.recipients.append(recipient)
        elif type(recipient) is list:
            self.recipients.update(recipient)

    def set_subject(self,subject):
        self.subject = subject
        try:
            del self.msg['Subject']
            self.msg['Subject'] = Header(self.subject, self.encoding)
        except:
            pass

    def set_body(self,body):
        self.body = body

    def reset_attach(self):
        self.attach = None

    def add_attach(self,attach):
        if self.attach is None:
            self.attach = []

        if type(attach) is str:
            self.attach.append(attach)
        elif type(attach) is list:
            self.attach.update(attach)

    def set_auth_user_passwd(self, user, passwd):
        self.auth_user   = user
        self.auth_passwd = passwd

    def create_message(self):

        if self.attach:
            self.create_multipart_message()
        else:
            self.create_text_message()

        """comment
        """
        charset = Charset(self.encoding)
        charset.header_encoding = QP
        charset.body_encoding = QP
        self.msg.set_charset(charset)
        """
        """

    def create_base_header(self):
        self.msg['Subject'] = Header(self.subject, self.encoding)
        self.msg['From']    = self.sender
        self.msg['To']      = ", ".join(self.recipients)
        self.msg['Date']    = formatdate()

    def create_text_message(self):
        self.msg = MIMEText(self.body, 'plain', self.encoding)
        self.create_base_header()
 
    def create_multipart_message(self):
        self.msg = MIMEMultipart('mixed')
        self.create_base_header()
        text_msg = MIMEText(self.body, 'plain', self.encoding)
        self.msg.attach(text_msg)

        for _attach in self.attach:
            content_type = guess_type(_attach)[0]
            if content_type is None:
                content_type = "application/octet-stream"

            main_type, sub_type = content_type.split('/', 1)
            
            _part = MIMEBase(main_type, sub_type)
            _part['Content-ID'] = _attach
            _part.set_payload(open(_attach).read())
            Encoders.encode_base64(_part)
            _part.__delitem__('Content-Type')
            _part.add_header('Content-Type', content_type, name=os.path.basename(_attach))
            self.msg.attach(_part)

    def send(self):

        if self.timeout is not None:
            if self.verbose is True:
                print "set timeout %d seconds" % self.timeout
            socket.setdefaulttimeout(self.timeout)

        try:
            s = smtplib.SMTP(self.smtp_server,self.smtp_port)
        except socket.error, msg:
            if self.verbose is True:
                print >>sys.stderr, "Error: %s." % msg
            raise MAIL_LIB_Exception("Error: %s." % msg)
        except:
            raise MAIL_LIB_Exception("Error: connection error")


        if self.tls is True:
            s.ehlo()
            if self.verbose is True:
                print "send starttls cmd..."
            s.starttls()
        if self.auth_user is not None and self.auth_passwd is not None:
            s.ehlo()
            if self.verbose is True:
                print "send login cmd..."
            s.login(self.auth_user, self.auth_passwd)

        if self.verbose is True:
            print "send mail to %s..." % ",".join(self.recipients)
        s.sendmail(self.sender, self.recipients, self.msg.as_string())
        s.close()

"""
subject = "root@localhost"
sender = "root@localhost"
recipient = "root@localhost"
attach = "/etc/hosts"
body = " tesst "
subject="foobar"
maillib = MAIL_LIB()
maillib.set_sender(sender)
maillib.set_recipients([recipient])
maillib.add_recipient("root")
maillib.set_subject(subject)
maillib.set_body(body)
maillib.add_attach(attach)
maillib.create_message()
maillib.send()
"""
