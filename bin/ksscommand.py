#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
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

import sys
import os
import os.path
import traceback
import logging

from __cmd__ import karesansui_conf, search_path, pysilhouette_conf

# init -- read file
if os.path.isfile(karesansui_conf) is False:
    print('[Error] karesansui : Initializing a database error - %s' % str(e), file=sys.stderr)
    sys.exit(1)

for y in [x.strip() for x in search_path.split(',') if x]:
    if (y in sys.path) is False: sys.path.insert(0, y)

try:
    import karesansui
    import pysilhouette
except ImportError:
    print('[Error] No libraries needed at runtime.(karesansui, pysilhouette)', file=sys.stderr)
    sys.exit(1)

from pysilhouette.command import Command, CommandException
from os import environ as env

import karesansui.db
import karesansui.lib.log.logger
from karesansui.lib.file.k2v import K2V

class KssCommandException(CommandException):
    pass

class KssCommandOptException(KssCommandException):
    pass

class KssCommand(Command):

    def __init__(self):
        # --
        try:
            _k2v = K2V(karesansui_conf)
            karesansui.config = _k2v.read()
        except Exception as e:
            print('[Error] Failed to load configuration file. - %s : msg=%s' % (karesansui_conf, str(e)), file=sys.stderr)
            sys.exit(1)

        karesansui.lib.log.logger.reload_conf(karesansui.config['application.log.config'])
        self.logger = logging.getLogger('karesansui.command')
        self.logger_trace = logging.getLogger('karesansui_trace.command')

        # PySilhouette - command.py#__init__()
        os.environ['PYSILHOUETTE_CONF'] = pysilhouette_conf
        Command.__init__(self)

        try:
            # Karesansui Database
            self.kss_db = karesansui.db.get_engine()
            self.kss_session = karesansui.db.get_session()
        except Exception as e:
            print('[Error] KssCommand : Initializing a database error.', file=sys.stderr)
            self.logger.error('Initializing a database error.')
            self.logger_trace.error(traceback.format_exc())
            sys.exit(1)

    def run(self):
        try:
            try:
                try:
                    if self._pre() is False:
                        raise KssCommandException("Error running in _pre().")
                    self.up_progress(10)

                    if self.process() is False:
                        raise KssCommandException("Error running in process().")
                    self.up_progress(10)

                    if self._post() is False:
                        raise KssCommandException("Error running in _post().")

                    self.up_progress(100)
                    return 0

                except KssCommandOptException as e:
                    self.logger.error("Karesansui : Command option error - %s" % str(e))
                    print("Karesansui : Command option error - %s" % str(e), file=sys.stderr)
                    return 2

                except KssCommandException as e:
                    self.logger.error("Karesansui : Command execution error - %s" % str(e))
                    print("Karesansui : Command execution error - %s" % str(e), file=sys.stderr)
                    raise

                except SystemExit as e:
                    self.session.rollback() # pysilhouette
                    self.kss_session.rollback()
                    return e.code

                except KeyboardInterrupt as e:
                    self.logger.error("Aborted by user request.")
                    print(_("Aborted by user request."), file=sys.stderr)
                    raise

            except Exception as e:
                #logging.exception(e)
                self.session.rollback() # pysilhouette
                self.kss_session.rollback()
                print(str(e), file=sys.stderr)
                self.logger_trace.error(traceback.format_exc())
                return 1

        finally:
            self.session.commit() # pysilhouette
            self.kss_session.commit()
