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

force=1
if [ "x$1" = "x-f" ]; then
  force=0
fi

__brctl=/usr/sbin/brctl
__ifconfig=/sbin/ifconfig

for brname in `brctl show | grep ^virbr | awk '{print $1}' | sed -e 's#^virbr##' | sort -n`
do
  brname=virbr${brname}
  if [ ${force} -eq 1 ]; then
    echo -n "Delete bridge ${brname}? [y/N]:"
    read answer
    if [ "x${answer}" != "xy" ]; then
      continue
    fi
  fi
  echo -n "delete bridge ${brname}... "
  ${__ifconfig} ${brname} down
  ${__brctl} delbr ${brname}
  echo "done"
done
