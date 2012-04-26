#!/bin/sh

OPT_ERROR=0
while getopts "l:" flag
do
  case $flag in
    \?) OPT_ERROR=1; break;;
    l) lang="$OPTARG";;
  esac
done
shift $(( $OPTIND - 1 ))
if [ $OPT_ERROR -ne 0 -o "x${lang}" = "x" ]; then
  echo >&2 "usage: $0 [-l lang]"
  exit 1
fi

make gettext

if [ ! -d locale/${lang}/LC_MESSAGES/ ]; then
  mkdir -p locale/${lang}/LC_MESSAGES/
fi

for pot_file in `ls -1 _build/locale/*.pot`
do
  pot_file_basename=`basename ${pot_file} | sed -e 's/\.pot$//'`
  po_file=locale/${lang}/LC_MESSAGES/${pot_file_basename}.po
  mo_file=locale/${lang}/LC_MESSAGES/${pot_file_basename}.mo

  if [ -f ${po_file} ]; then
    echo -n "${pot_file_basename}... "
    msgmerge --update ${po_file} ${pot_file}
  else
    msginit --locale=${lang} --input=${pot_file} --output=${po_file}
  fi
  msgfmt ${po_file} -o ${mo_file}
done

touch *.rst
make html
