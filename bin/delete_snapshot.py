#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

""" 
<description>

@file:   delete_snapshot.py
@author: Taizo ITO <taizo.ito@karesansui-project.info>
@copyright:    

<comment-ja>
ゲストOSの指定したスナップショットを削除する

 使用方法: delete_snapshot.py [オプション]

  オプション:
    --version             プログラムのバージョンを表示
    -h, --help            使用方法を表示
    -n NAME, --name=NAME  ドメイン名を指定
    -i ID, --id=ID        スナップショットのIDを指定
</comment-ja>
<comment-en>
Delete a snapshot from the domain.

 usage: delete_snapshot.py [options]

  options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -n NAME, --name=NAME  Domain name
    -i ID, --id=ID        Snapshot serial ID
</comment-en>
"""

import os
import os.path
import sys
import logging
import traceback
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
    from karesansui.lib.utils import load_locale
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain name'))
    optp.add_option('-i', '--id', dest='id', help=_('Snapshot serial ID'))
    return optp.parse_args()

def chkopts(opts):
    if not opts.name:
        raise KssCommandOptException('ERROR: -n or --name option is required.')

    if not opts.id:
        raise KssCommandOptException('ERROR: -i or --id option is required.')

class DeleteSnapshot(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        kvs = KaresansuiVirtSnapshot(readonly=False)
        try:
            self.up_progress(10)
            try:
                domain = kvs.whichDomain(opts.id)
                if len(domain) == 0:
                    msg = _("Snapshot '%s' not found in domain '%s'.") % (opts.id,opts.name,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                if not opts.name in domain:
                    msg = _("Snapshot '%s' not found in domain '%s'.") % (opts.id,opts.name,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                ret = kvs.deleteSnapshot(opts.id)
                if ret is False:
                    msg = _("Can't delete snapshot '%s'.") % (opts.id,)
                    self.logger.error(msg)
                    raise KssCommandException(msg)

                self.up_progress(50)

                msg = _("Domain snapshot '%s' deleted.") % (opts.id,)
                self.logger.info(msg)
                print >>sys.stdout, msg

            except KssCommandException, e:
                raise KssCommandException(''.join(e.args))
            except Exception, e:
                msg = _("Failed to delete snapshot '%s'.") % (opts.id,)
                msg += ": detail %s" % ''.join(e.args)
                self.logger.error(msg)
                raise KssCommandException(msg)

        finally:
            kvs.finish()

        return True

if __name__ == "__main__":
    target = DeleteSnapshot()
    sys.exit(target.run())
