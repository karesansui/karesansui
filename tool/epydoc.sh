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

uniq_id=$$
locale=en
locale=ja

py_ver=`python -c 'import sys;print sys.version[:3]'`
vendor_prefix=/usr
vendor_sysconfdir=/etc
vendor_pysitedir=${vendor_prefix}/lib/python2.6/site-packages

karesansui_pysitedir=${vendor_prefix}/lib/python2.6/site-packages

export PATH=${PATH}:${vendor_prefix}/bin
export PYTHONPATH=${karesansui_pysitedir}.${uniq_id}:${vendor_pysitedir}:${PYTHONPATH}

script_dir=`dirname $0`
pushd $script_dir >/dev/null 2>&1
# shell directory.
script_dir=`pwd`
popd >/dev/null 2>&1

epydoc_config=${script_dir}/../doc/epydoc.cfg

___realpath() {
  if [ ! -e "$1" ]; then
    return 1
  fi
  pushd `dirname $1` >/dev/null 2>&1
  rdir=`pwd`
  popd >/dev/null 2>&1
  filename=${rdir}"/"`basename $1`
  if [ -L ${filename} ]; then
    path=`ls -ld ${filename} 2>/dev/null | sed -e "s%.* ${filename} -> \(.*\)$%\\1%"`
    echo ${path} | grep "^/" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      ___realpath ${path}
    else
      ___realpath ${rdir}/${path}
    fi
  else
    echo ${filename}
  fi
  return 0
}

___exit() {
  rm -f  ${epydoc_config}.${uniq_id}
  #rm -rf ${vendor_pysitedir}.${uniq_id}
  rm -rf ${karesansui_pysitedir}.${uniq_id}
  exit $1
}

trap '___exit 1' 1 2 3 15

rpm -q lighttpd >/dev/null 2>&1
if [ $? -eq 0 ]; then
  lighttpd_conf=${vendor_sysconfdir}/lighttpd/lighttpd.conf
  grep -- karesansui-doc ${lighttpd_conf} >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "alias.url = (\"/karesansui-doc/\" => \"${vendor_prefix}/www/karesansui-doc/\")" \
      >>${lighttpd_conf}
  fi
  target=${vendor_prefix}/www/karesansui-doc
else
  target=/var/www/html/karesansui-doc
fi

if [ -e ${target} ]; then
  rm -fr ${target}
fi
mkdir -p ${target}

#mkdir -p ${vendor_pysitedir}.${uniq_id}
mkdir -p ${karesansui_pysitedir}.${uniq_id}


if [ "${locale}" = "ja" ]; then
  exclude_locale=en
else
  exclude_locale=ja
fi
#project_pysitedir=`___realpath ${vendor_pysitedir}/karesansui`
project_pysitedir=`___realpath ${karesansui_pysitedir}/karesansui`
#cp -frp ${project_pysitedir} ${vendor_pysitedir}.${uniq_id}/
cp -frp ${project_pysitedir} ${karesansui_pysitedir}.${uniq_id}/
#for afile in `find ${vendor_pysitedir}.${uniq_id} -name "*.py"`
for afile in `find ${karesansui_pysitedir}.${uniq_id} -name "*.py"`
do
  echo $afile
  sed \
      -e 's/\(<comment-[a-z]*\)/\n\1/' \
      -e 's/\(<\/comment-[a-z]*>\)/\1\n/' \
   ${afile} | sed \
      -e "/<comment-${exclude_locale}>/,/<\/comment-${exclude_locale}>/d" \
      -e "s/<comment-${locale}>//" \
      -e "s/<\/comment-${locale}>//" \
   > ${afile}.$$
  mv -f ${afile}.$$ ${afile}
done


dotpath=/usr/bin/dot
if [ -e ${vendor_prefix}/bin/dot ]; then
  dotpath=${vendor_prefix}/bin/dot
fi

sed \
  -e "s#^target:.*#target: ${target}#" \
  -e "s#^dotpath: .*#dotpath: ${dotpath}#" \
 ${epydoc_config} >${epydoc_config}.${uniq_id}

epydoc --config ${epydoc_config}.${uniq_id}

___exit 0
