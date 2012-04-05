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

export PYTHONPATH=/usr/lib/python:/usr/lib/python2.6
export PATH=$PATH:/usr/bin:/bin

__sed=`which sed`
__time=`date '+%Y%m%d%H%M%S'`

script_dir=`dirname $0`
pushd ${script_dir} >/dev/null 2>&1
# shell directory.
script_dir=`pwd`
popd >/dev/null 2>&1
pushd ${script_dir}/../ >/dev/null 2>&1
home_dir=`pwd`
popd >/dev/null 2>&1


OPT_ERROR=0
while getopts "c:" flag
do
  case $flag in
    \?) OPT_ERROR=1; break;;
    c) add_comments="$OPTARG";;
  esac
done
shift $(( $OPTIND - 1 ))
if [ $OPT_ERROR -ne 0 ]; then
  echo >&2 "usage: $0 [-c comment_for_translator]"
  exit 1
fi
extract_opts=
if [ "x${add_comments}" != "x" ]; then
  extract_opts="${extract_opts} --add-comments=${add_comments}"
fi

# extract options
#
# --charset=CHARSET      charset to use in the output
# --keyword=KEYWORDS     keywords to look for in addition to the defaults.
# --no-default-keywords  don't include the default keywords
# --mapping=MAPPING_FILE path to the extraction mapping file
# --no-location          don't include location comments with filename and lnum
# --omit-header          don't include msgid "" entry in header
# --output=OUTPUT        path to the output POT file
# --width=WIDTH          set output line width (default 76)
# --no-wrap              do not break long message lines
# --sort-output          generate sorted output (default False)
# --sort-by-file         sort output by file location (default False)
# --msgid-bugs-address=EMAIL@ADDRESS  set report address for msgid
# --copyright-holder=COPYRIGHT_HOLDER set copyright holder in output
# --strip-comment-tags   strip the comment tags from the comments.
#
#extract_opts="${extract_opts} --no-default-keywords --keyword=_"
#extract_opts="${extract_opts} --no-location --sort-output"

update_opts=
# update options
#
# --domain=DOMAIN     domain of PO file (default 'messages')
# --input-file=FILE   name of the input file
# --output-dir=DIR    path to output directory
# --output-file=FILE  name of the output file
# --locale=LOCALE     locale of the translations catalog
# --ignore-obsolete   don't include obsolete messages in the output
# --no-fuzzy-matching don't use fuzzy matching (default False)
# --previous          keep previous msgids of translated messages(default False)

echo "########################################################"
echo "    Karesansui Project                                      "
echo "            Babel (Internationalization) execute        "
echo "########################################################"
echo
echo "!!!!!!!!!!!!!!  Press <ENTER> to continue convert. !!!!!!!!!!!!!!!!!!!!"
echo "!!!!!!!!!!!!!!!!!!!!!!  Ctrl-C for aborting  !!!!!!!!!!!!!!!!!!!!!!!!!!"
read
echo
echo 

echo -n "Please input karesansui home directory(default:${home_dir}): "
read current_dir
if [ "x${current_dir}" = "x" ]; then
  current_dir=${home_dir}
fi

__pybabel=`which pybabel >/dev/null 2>&1`
if [ $? -eq 1 ]; then
  echo "Error:Babel(python) library is not installed."
  exit 1
fi

__babel_map="${home_dir}/doc/babel.map"
echo -n "Please input path to the extraction mapping file(default:${__babel_map}): "
read map
if [ "x${map}" = "x" ]; then
  map=${__babel_map}
fi

__messages_pot="${home_dir}/doc/messages.pot"
echo -n "Please input path to the extraction mapping file(default:${__messages_pot}): "
read pot
if [ "x${pot}" = "x" ]; then
  pot=${__messages_pot}
fi

target_dir="${home_dir}/karesansui"
locale_dir="${target_dir}/locale"
ja_po="${locale_dir}/ja/LC_MESSAGES/messages.po"
en_po="${locale_dir}/en/LC_MESSAGES/messages.po"

if [ -f "${pot}" ]; then
  if [ -f ${ja_po} ]; then
    pybabel update -l ja -i ${pot} -d ${locale_dir} ${update_opts}
  else
    pybabel init -l ja -i ${pot} -d ${locale_dir}
  fi

  if [ -f ${en_po} ]; then 
    pybabel update -l en -i ${pot} -d ${locale_dir} ${update_opts}
  else
    pybabel init -l en -i ${pot} -d ${locale_dir}
  fi
else
  pybabel extract -F ${map} -o ${pot} ${extract_opts} ${home_dir}
  echo "Please execute it again."
  exit 1
fi

# create .mo
pybabel compile -d ${locale_dir} -f
