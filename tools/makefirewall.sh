#!/bin/bash
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
#
# usage: makefirewall.sh domU
#

__xm=/usr/sbin/xm
__virsh=/usr/bin/virsh
__iptables=/sbin/iptables

if [ ! -x ${__virsh} -o ! -x ${__iptables} ]; then
  echo "ERROR: ${__virsh} or ${__iptables} is not executable." >&2
  exit 1
fi

#domain_id=`${__xm} list $1 2>/dev/null | grep "$1" | awk '{print $2}'`
domain_id=`${__virsh} dominfo $1 2>/dev/null | grep ^Id: | awk '{print $2}'`
if [ "x${domain_id}" = "x" ]; then
  echo "ERROR: domain $1 not found." >&2
  exit 1
fi

chain_name="DOM_$1"

${__iptables} -N "${chain_name}"
${__iptables} -I FORWARD -m physdev  --physdev-in peth0 --physdev-out vif${domain_id}.0 -j "${chain_name}"
${__iptables} -A "${chain_name}" -p tcp -j LOG 
${__iptables} -A "${chain_name}" -p tcp -m tcp --dport 22 -j RETURN 
${__iptables} -A "${chain_name}" -p tcp -m state --state RELATED,ESTABLISHED -j RETURN 
${__iptables} -A "${chain_name}" -p tcp -j DROP

echo "Done creating firewall for ${chain_name}"

