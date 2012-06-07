#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
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
import os.path
import sys
import re
import time
import signal
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale
    from karesansui.lib.utils import copy_file
    from karesansui.lib.utils import execute_command
    from karesansui.lib.utils import preprint_r, base64_decode
    from karesansui.lib.collectd.config import initialize_collectd_settings, COLLECTD_PLUGINS
    from karesansui.lib.dict_op import DictOp

except ImportError, e:
    print >>sys.stderr, "[Error] some packages not found. - %s" % e
    sys.exit(1)

_ = load_locale()


"""
initialize_collectd_conf.py -T --post-command "/etc/init.d/collectd condrestart"
"""

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-q', '--quiet',dest='verbose', action="store_false", default=True, help=_("don't print status messages"))
    optp.add_option('-j', '--pre-command',  dest='pre_command',  default=None, help=_('Scriptlet to execute before writing.'))
    optp.add_option('-J', '--post-command',  dest='post_command',  default=None, help=_('Scriptlet to execute after writing.'))
    optp.add_option('-F', '--force',  dest='force',  action="store_true", default=False, help=_("Force to initialize. Reset to default value."))
    optp.add_option('-R', '--reverse',  dest='reverse',  action="store_true", default=False, help=_("Disable each plugin."))
    optp.add_option('-T', '--dry-run',  dest='dry_run',  action="store_true", default=False, help=_("Don't do anything, just test."))

    return optp.parse_args()

def chkopts(opts):
    pass

class InitializeCollectdConf(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(1)

        uniq_id = time.strftime("%Y%m%d%H%M%S", time.localtime())

        if opts.pre_command is not None:
            if opts.pre_command[0:4] == "b64:":
                command = base64_decode(opts.pre_command[4:])
            else:
                command = opts.pre_command
            self.logger.info("execute command - %s" % command)

            if opts.dry_run is True:
                print ""
                print ">>>Execute pre command: %s" % command
                print ""
            else:
                (_ret,_res) = execute_command(command.split())
                if _ret != 0:
                    error_msg = "execute error - %s" % command
                    self.logger.error(error_msg)
                    #raise KssCommandOptException("ERROR: %s" % error_msg)

        self.up_progress(5)

        from karesansui.lib.parser.collectd       import collectdParser
        from karesansui.lib.parser.collectdplugin import collectdpluginParser
        dop = DictOp()

        collectd_parser       = collectdParser()
        dop.addconf("collectd",collectd_parser.read_conf())

        collectdplugin_parser = collectdpluginParser()
        extra_args = {"include":"^(%s)$" % "|".join(COLLECTD_PLUGINS)}
        dop.addconf("collectdplugin",collectdplugin_parser.read_conf(extra_args=extra_args))

        initialize_collectd_settings(dop=dop,force=opts.force,reverse=opts.reverse)

        retval = collectd_parser.write_conf(dop.getconf("collectd"),dryrun=opts.dry_run)
        retval = collectdplugin_parser.write_conf(dop.getconf("collectdplugin"),extra_args=extra_args,dryrun=opts.dry_run)

        self.up_progress(30)

        if opts.post_command is not None:
            if opts.post_command[0:4] == "b64:":
                command = base64_decode(opts.post_command[4:])
            else:
                command = opts.post_command
            self.logger.info("execute command - %s" % command)

            if opts.dry_run is True:
                print ""
                print ">>>Execute post command: %s" % command
                print ""
            else:
                (_ret,_res) = execute_command(command.split())
                if _ret != 0:
                    error_msg = "execute error - %s" % command
                    self.logger.error(error_msg)
                    raise KssCommandOptException("ERROR: %s" % error_msg)

        self.up_progress(10)
        return True

if __name__ == "__main__":
    target = InitializeCollectdConf()
    sys.exit(target.run())
