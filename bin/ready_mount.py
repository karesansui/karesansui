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
import sys
import re
import logging
import fcntl
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException
import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import load_locale, execute_command, pipe_execute_command, generate_phrase, get_filesystem_info
    from karesansui.lib.const import KARESANSUI_TMP_DIR, MOUNT_CMD, UMOUNT_CMD, FORMAT_CMD, YES_CMD

except ImportError as e:
    print("[Error] some packages not found. - %s" % e, file=sys.stderr)
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-d', '--dev', dest='dev', help=_('Target device'), default=None)
    optp.add_option('-t', '--type', dest='type', help=_('Format type'), default="ext3")
    optp.add_option('-f', '--format', dest='format', action="store_true", help=_('Format on mount failed'), default=False)
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.dev:
        if reg.search(opts.dev):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-d or --dev', opts.dev))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-d or --dev')

    if opts.type not in get_filesystem_info():
        raise KssCommandOptException('ERROR: Unknown format type. type=%s' % (opts.type))

class ReadyMount(KssCommand):

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)

        self.up_progress(10)
        try:
            tmp_dir_name = generate_phrase(12,'abcdefghijklmnopqrstuvwxyz')
            tmp_dir_path = "%s/%s" % (KARESANSUI_TMP_DIR, tmp_dir_name)
            os.mkdir(tmp_dir_path)
        except:
            raise KssCommandException('Failed to make tmpdir. path=%s' % (tmp_dir_path))

        try:
            self.up_progress(10)
            mount_command_args = (MOUNT_CMD,
                                  opts.dev,
                                  tmp_dir_path,
                                  )
            umount_command_args = (UMOUNT_CMD,
                                   tmp_dir_path,
                                   )

            is_mountable = False
            try:
                (mount_cmd_rc, mount_cmd_res) = execute_command(mount_command_args)
                if mount_cmd_rc == 0:
                    is_mountable = True
                else:
                    self.logger.debug('Failed to mount. dev=%s' % (opts.dev))
            finally:
                (umount_cmd_rc, umount_cmd_res) = execute_command(umount_command_args)

            self.up_progress(30)
            if is_mountable is False and opts.format is True:
                first_command_args = YES_CMD
                second_command_args = (FORMAT_CMD,
                                       "-t",
                                       opts.type,
                                       opts.dev,
                                       )
                format_command_args = (first_command_args,
                                       second_command_args,
                                       )

                (format_cmd_rc, format_cmd_res) = pipe_execute_command(format_command_args)
                if format_cmd_rc != 0:
                    raise KssCommandException('Failed to format. dev=%s type=%s res=%s' % (opts.dev, opts.type, format_cmd_res))

                try:
                    (mount_cmd_rc, mount_cmd_res) = execute_command(mount_command_args)
                    if mount_cmd_rc == 0:
                        is_mountable = True
                    else:
                        self.logger.debug('Failed to mount. dev=%s' % (opts.dev))
                finally:
                    (umount_cmd_rc, umount_cmd_res) = execute_command(umount_command_args)

            self.up_progress(40)

        finally:
            try:
                os.rmdir(tmp_dir_path)
            except:
                raise KssCommandException('Failed to delete tmpdir. path=%s' % (tmp_dir_path))

        if is_mountable is True:
            self.logger.info('Device "%s" is mountable.' % (opts.dev))
            print(_('Device "%s" is mountable.' % (opts.dev)), file=sys.stdout)
        else:
            self.logger.info('Device "%s" is not mountable.' % (opts.dev))
            print(_('Device "%s" is not mountable.' % (opts.dev)), file=sys.stdout)

        return is_mountable

if __name__ == "__main__":
    target = ReadyMount()
    sys.exit(target.run())
