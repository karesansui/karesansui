#!/bin/sh
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

KARESANSUI_CONF=/etc/karesansui/application.conf
#SEARCH_PATH=/usr/lib/python:/usr/lib/python2.6
PYTHONPATH=/usr/lib/python:/usr/lib/python2.6
FCGI=True

#export PYTHONPATH SEARCH_PATH KARESANSUI_CONF
export PYTHONPATH KARESANSUI_CONF FCGI

which trace2html.py >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo 'error: trace2html.py not found.' >&2
  exit 1
fi

pushd /var/lib/karesansui/www >/dev/null 2>&1
rm -fr coverage_dir
echo `env`
trace2html.py -w karesansui --run-command /usr/lib/python2.6/site-packages/karesansui/tests/suite.py
popd >/dev/null 2>&1

echo
echo 'Go to "http://localhost/coverage_dir/".'
