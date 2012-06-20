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

import web

import karesansui.gadget.index
import karesansui.gadget.data
import karesansui.gadget.user
import karesansui.gadget.userby1
import karesansui.gadget.me
import karesansui.gadget.job
import karesansui.gadget.logout
import karesansui.gadget.tree
import karesansui.gadget.console
import karesansui.gadget.mail
import karesansui.gadget.tag
import karesansui.gadget.msg
import karesansui.gadget.icon
import karesansui.gadget.about
import karesansui.gadget.host
import karesansui.gadget.hosttag
import karesansui.gadget.hostby1
import karesansui.gadget.hostby1job
import karesansui.gadget.hostby1firewall
import karesansui.gadget.hostby1firewallstatus
import karesansui.gadget.hostby1firewallpolicy
import karesansui.gadget.hostby1firewallrule
import karesansui.gadget.hostby1firewallruleby1
import karesansui.gadget.hostby1network
import karesansui.gadget.hostby1networkby1
import karesansui.gadget.hostby1networkby1status
import karesansui.gadget.hostby1setting
import karesansui.gadget.hostby1settingby1mail
import karesansui.gadget.hostby1settingby1proxy
import karesansui.gadget.hostby1networkstorage
import karesansui.gadget.hostby1networkstorageby1
import karesansui.gadget.hostby1networkstorageby1status
import karesansui.gadget.hostby1storagepool
import karesansui.gadget.hostby1storagepoolby1
import karesansui.gadget.hostby1storagepoolby1status
import karesansui.gadget.hostby1networksettings
import karesansui.gadget.hostby1networksettingsgeneral
import karesansui.gadget.hostby1networksettingsnicby1
import karesansui.gadget.hostby1iptables
import karesansui.gadget.hostby1iptablesstatus
import karesansui.gadget.hostby1staticroute
import karesansui.gadget.hostby1staticrouteby1
import karesansui.gadget.hostby1report
import karesansui.gadget.hostby1reportby1
import karesansui.gadget.hostby1reportby1by1
import karesansui.gadget.hostby1watch
import karesansui.gadget.hostby1watchby1
import karesansui.gadget.hostby1watchtemplate
import karesansui.gadget.hostby1service
import karesansui.gadget.hostby1serviceby1
import karesansui.gadget.hostby1serviceby1status
import karesansui.gadget.hostby1log
import karesansui.gadget.hostby1logby1
import karesansui.gadget.hostby1logby1appby1
import karesansui.gadget.guest
import karesansui.gadget.guesttag
import karesansui.gadget.guestreplicate
import karesansui.gadget.guestexport
import karesansui.gadget.guestexportby1
import karesansui.gadget.guestimport
import karesansui.gadget.guestby1
import karesansui.gadget.guestby1status
import karesansui.gadget.guestby1device
import karesansui.gadget.guestby1diskby1
import karesansui.gadget.guestby1nicby1
import karesansui.gadget.guestby1cpu
import karesansui.gadget.guestby1memory
import karesansui.gadget.guestby1graphics
import karesansui.gadget.guestby1snapshot
import karesansui.gadget.guestby1snapshotby1
import karesansui.gadget.guestby1currentsnapshot
import karesansui.gadget.guestby1job
import karesansui.gadget.uriguestby1
import karesansui.gadget.uriguestby1status
import karesansui.gadget.init

#: URL List
urls = karesansui.gadget.index.urls \
       + karesansui.gadget.data.urls \
       + karesansui.gadget.user.urls \
       + karesansui.gadget.userby1.urls \
       + karesansui.gadget.me.urls \
       + karesansui.gadget.job.urls \
       + karesansui.gadget.logout.urls \
       + karesansui.gadget.tree.urls \
       + karesansui.gadget.console.urls \
       + karesansui.gadget.mail.urls \
       + karesansui.gadget.tag.urls \
       + karesansui.gadget.msg.urls \
       + karesansui.gadget.icon.urls \
       + karesansui.gadget.about.urls \
       + karesansui.gadget.host.urls \
       + karesansui.gadget.hosttag.urls \
       + karesansui.gadget.hostby1.urls \
       + karesansui.gadget.hostby1job.urls \
       + karesansui.gadget.hostby1firewall.urls \
       + karesansui.gadget.hostby1firewallstatus.urls \
       + karesansui.gadget.hostby1firewallpolicy.urls \
       + karesansui.gadget.hostby1firewallrule.urls \
       + karesansui.gadget.hostby1firewallruleby1.urls \
       + karesansui.gadget.hostby1network.urls \
       + karesansui.gadget.hostby1networkby1.urls \
       + karesansui.gadget.hostby1networkby1status.urls \
       + karesansui.gadget.hostby1setting.urls \
       + karesansui.gadget.hostby1settingby1mail.urls \
       + karesansui.gadget.hostby1settingby1proxy.urls \
       + karesansui.gadget.hostby1networkstorage.urls \
       + karesansui.gadget.hostby1networkstorageby1.urls \
       + karesansui.gadget.hostby1networkstorageby1status.urls \
       + karesansui.gadget.hostby1storagepool.urls \
       + karesansui.gadget.hostby1storagepoolby1.urls \
       + karesansui.gadget.hostby1storagepoolby1status.urls \
       + karesansui.gadget.hostby1networksettings.urls \
       + karesansui.gadget.hostby1networksettingsgeneral.urls \
       + karesansui.gadget.hostby1networksettingsnicby1.urls \
       + karesansui.gadget.hostby1iptables.urls \
       + karesansui.gadget.hostby1iptablesstatus.urls \
       + karesansui.gadget.hostby1staticroute.urls \
       + karesansui.gadget.hostby1staticrouteby1.urls \
       + karesansui.gadget.hostby1report.urls \
       + karesansui.gadget.hostby1reportby1.urls \
       + karesansui.gadget.hostby1reportby1by1.urls \
       + karesansui.gadget.hostby1watch.urls \
       + karesansui.gadget.hostby1watchby1.urls \
       + karesansui.gadget.hostby1watchtemplate.urls \
       + karesansui.gadget.hostby1service.urls \
       + karesansui.gadget.hostby1serviceby1.urls \
       + karesansui.gadget.hostby1serviceby1status.urls \
       + karesansui.gadget.hostby1log.urls \
       + karesansui.gadget.hostby1logby1.urls \
       + karesansui.gadget.hostby1logby1appby1.urls \
       + karesansui.gadget.guest.urls \
       + karesansui.gadget.guesttag.urls \
       + karesansui.gadget.guestreplicate.urls \
       + karesansui.gadget.guestexport.urls \
       + karesansui.gadget.guestexportby1.urls \
       + karesansui.gadget.guestimport.urls \
       + karesansui.gadget.guestby1.urls \
       + karesansui.gadget.guestby1status.urls \
       + karesansui.gadget.guestby1device.urls \
       + karesansui.gadget.guestby1diskby1.urls \
       + karesansui.gadget.guestby1nicby1.urls \
       + karesansui.gadget.guestby1cpu.urls \
       + karesansui.gadget.guestby1memory.urls \
       + karesansui.gadget.guestby1graphics.urls \
       + karesansui.gadget.guestby1snapshot.urls \
       + karesansui.gadget.guestby1snapshotby1.urls \
       + karesansui.gadget.guestby1currentsnapshot.urls \
       + karesansui.gadget.guestby1job.urls \
       + karesansui.gadget.uriguestby1.urls \
       + karesansui.gadget.uriguestby1status.urls \
       + karesansui.gadget.init.urls \


if web.wsgi._is_dev_mode() is True:
    import karesansui.gadget.static
    urls += karesansui.gadget.static.urls
