#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

import sys
import os
import os.path
import traceback
import logging

from __cmd__ import karesansui_conf, search_path, pysilhouette_conf

# init -- read file
if os.path.isfile(karesansui_conf) is False:
    print >>sys.stderr, '[Error] karesansui : Initializing a database error - %s' % str(e)
    sys.exit(1)

for y in [x.strip() for x in search_path.split(',') if x]:
    if (y in sys.path) is False: sys.path.insert(0, y)

try:
    import karesansui
    import pysilhouette
except ImportError:
    print >>sys.stderr, '[Error] No libraries needed at runtime.(karesansui, pysilhouette)'
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
        except Exception, e:
            print >>sys.stderr, '[Error] Failed to load configuration file. - %s : msg=%s' % (karesansui_conf, str(e))
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
        except Exception, e:
            print >>sys.stderr, '[Error] KssCommand : Initializing a database error.'
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

                except KssCommandOptException, e:
                    self.logger.error("Karesansui : Command option error - %s" % str(e))
                    print >>sys.stderr, "Karesansui : Command option error - %s" % str(e)
                    return 2

                except KssCommandException, e:
                    self.logger.error("Karesansui : Command execution error - %s" % str(e))
                    print >>sys.stderr, "Karesansui : Command execution error - %s" % str(e)
                    raise

                except SystemExit, e:
                    self.session.rollback() # pysilhouette
                    self.kss_session.rollback()
                    return e.code

                except KeyboardInterrupt, e:
                    self.logger.error("Aborted by user request.")
                    print >> sys.stderr, _("Aborted by user request.")
                    raise

            except Exception, e:
                #logging.exception(e)
                self.session.rollback() # pysilhouette
                self.kss_session.rollback()
                print >> sys.stderr, str(e)
                self.logger_trace.error(traceback.format_exc())
                return 1

        finally:
            self.session.commit() # pysilhouette
            self.kss_session.commit()
