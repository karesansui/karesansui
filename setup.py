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

from distutils.core import setup
from karesansui import __app__, __version__, __release__

import os
scripts=['scripts/karesansui.fcgi']
for (root, dirs, files) in os.walk('bin'):
  for f in files:
    scripts.append("%s" % (os.path.join(root, f),))

setup(name=__app__,
    version= '%s.%s' % (__version__, __release__),
    description='Virtualization management tool(Web Application)',
    long_description="""On the Web for virtualization management software to manage.
    The guest OS and the management of resources and dynamic changes can be done easily.
    RESTful Web applications in architecture.
    """,
    author='Taizo Ito',
    author_email='taizo@karesansui-project.info',
    maintainer='Taizo Ito',
    maintainer_email='taizo@karesansui-project.info',
    url='http://karesansui-project.info',
    download_url='',
    packages=['karesansui',
              'karesansui.db',
              'karesansui.db.access',
              'karesansui.db.model',
              'karesansui.gadget',
              'karesansui.lib',
              'karesansui.lib.collectd',
              'karesansui.lib.collectd.action',
              'karesansui.lib.file',
              'karesansui.lib.firewall',
              'karesansui.lib.log',
              'karesansui.lib.net',
              'karesansui.lib.parser',
              'karesansui.lib.parser.base',
              'karesansui.lib.rrd',
              'karesansui.lib.service',
              'karesansui.lib.virt',
              'karesansui.plus',
              'karesansui.tests',
              'karesansui.tests.lib',
    ],
    package_data={'':['locale/*/LC_MESSAGES/*.mo',
                      'templates/*/*/*.html',
                      'templates/*/*/*.xml',
                      'templates/*/*/*.json',
                      'templates/*/*/*.part',
                      'templates/*/*/*.input',
                      'templates/*/*/*.tmpl',
                      'templates/*/data/js/*.js',
                      'static/css/*',
                      'static/icon/*',
                      'static/images/*',
                      'static/java/*',
                      'static/js/*.js',
                      'static/lib/*.css',
                      'static/lib/*.js',
                      'static/lib/jquery.ui/i18n/*.js',
                      'static/lib/jquery.ui/*.js',
                      'static/lib/jquery.ui/themes/images/*.png',
                      'static/lib/jquery.ui/themes/*.css',
                      ]},
    scripts=scripts,
    license='The MIT License',
    keywords='',
    platforms='Linux',
    classifiers=['Development Status :: 5 - Production/Stable', 
                 'Environment :: Web Environment',
                 'Environment :: Console',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: Japanese',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Topic :: System :: Systems Administration'],
)
