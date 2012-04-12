#!/bin/sh

OPT_ERROR=0
while getopts "b:i:" flag
do
  case $flag in
    \?) OPT_ERROR=1; break;;
    b) database_bind="$OPTARG";;
    i) input_file="$OPTARG";;
  esac
done

shift $(( $OPTIND - 1 ))

if [ $OPT_ERROR -ne 0 -o "x${input_file}" = "x" -o "x${database_bind}" = "x" ]; then
  echo >&2 "usage: $0 -b database_bind -i input_file"
  exit 1
fi

if [ ! -f ${input_file} ]; then
  echo >&2 "error: ${input_file} not found."
  exit 1
fi

#database.bind=sqlite:////var/lib/karesansui/karesansui.db
#database_bind=mysql://localhost:3306/karesansui?charset=utf8
#database_bind=mysql://user:passwd@localhost:3306/karesansui?charset=utf8
#database_bind=mysql://localhost/karesansui?charset=utf8

echo "${database_bind}" | grep "^[a-z]*:.*$" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo >&2 "error: invalid format in 'database.bind'."
  exit 1
fi

db_type=`echo "${database_bind}" | awk -F: '{print $1}'`
db_path=`echo "${database_bind}" | sed -e 's#^[a-z]*:##'`

case "${db_type}" in
  "sqlite")
     db_path=`echo "${db_path}" | sed -e 's#^///##'`
     if [ ! -f "${db_path}" ]; then
       echo >&2 "error: '${db_path}' not found."
       exit 1
     fi

     grep ' MySQL dump' ${input_file} >/dev/null 2>&1
     if [ $? -eq 0 ]; then
       grep -v '^\-\-' ${input_file} | grep -v '^\/\*' | sqlite3 ${db_path}
     else
       cat "${input_file}" | sqlite3 ${db_path}
     fi
     break;;

  "mysql")
     db_path=`echo "${db_path}" | sed -e 's#^//##'`
     db_hostport=`echo "${db_path}" | awk -F'/' '{print $1}'`
     echo "${db_hostport}" | grep '@' >/dev/null 2>&1
     if [ $? -eq 0 ]; then
       db_userpass=`echo "${db_hostport}" | awk -F'@' '{print $1}'`
       db_hostport=`echo "${db_hostport}" | awk -F'@' '{print $2}'`
       db_user=`echo "${db_userpass}" | awk -F: '{print $1}'`
       echo "${db_userpass}" | grep ':' >/dev/null 2>&1
       if [ $? -eq 0 ]; then
         db_pass=`echo "${db_userpass}" | sed -e 's#^[a-z]*:##'`
       fi
     fi
     db_host=`echo "${db_hostport}" | awk -F: '{print $1}'`
     db_port=`echo "${db_hostport}" | awk -F: '{print $2}'`
     db_name=`echo "${db_path}" | awk -F'/' '{print $2}' | sed -e 's#\?.*$##'`
     #echo "db_user:"$db_user
     #echo "db_pass:"$db_pass
     #echo "db_host:"$db_host
     #echo "db_port:"$db_port
     #echo "db_name:"$db_name
     args=
     if [ "x${db_user}" != "x" ]; then
       args=$args" --user "${db_user}
     fi
     if [ "x${db_pass}" != "x" ]; then
       args=$args" --password "${db_pass}
     fi
     if [ "x${db_host}" != "x" ]; then
       args=$args" --host "${db_host}
     fi
     if [ "x${db_port}" != "x" ]; then
       args=$args" --port "${db_port}
     fi

     grep 'BEGIN TRANSACTION' ${input_file} >/dev/null 2>&1
     if [ $? -eq 0 ]; then
       sed \
         -e "s#^BEGIN TRANSACTION;#CREATE DATABASE ${dbname};\nuse ${dbname};\n#" \
         -e "s#^COMMIT;##" \
         -e "s#^INSERT INTO \"\([^ ]*\)\"#INSERT INTO \1#" \
         ${input_file} | mysql ${args} ${db_name}
     else
       mysql ${args} ${db_name} <${input_file}
     fi

     break;;
esac

#sqlite3 /var/lib/karesansui/karesansui.db .dump >dump.sql
#mysqldump -u username -h hostname -p password -P port karesansui >dump.sql
#mysqldump --user username --host hostname --password password --port port karesansui >dump.sql
#pg_dump -u -h hostname -p port karesansui >dump.sql
#pg_dump -u --host hostname --port port karesansui >dump.sql

#sqlite3 /var/lib/karesansui/karesansui.db .read dump.sql
#cat dump.sql | sqlite3 /var/lib/karesansui/karesansui.db
#mysql -u username -h hostname -p password -P port karesansui <dump.sql
#mysql --user username --host hostname --password password --port port karesansui <dump.sql
#psql --host hostname --port port --username username --password password --dbname karesansui -f dump.sql
#psql -h hostname -p port -U username -W password -d karesansui -f dump.sql


#sqlite
#BEGIN TRANSACTION;

#mysql
#-- MySQL dump 10.11
