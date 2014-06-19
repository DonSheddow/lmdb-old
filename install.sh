#!/bin/bash

# Prerequisites:
#
# apache2
#   libapache2-mod-python
#
# postgresql
#
# python
#   psycopg2
#   pyinotify
# 

if [ -d /opt/lmdb ]; then
  echo "lmdb seems to be installed already. Aborting... "
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <src_dir>"
  exit 1
fi; src_dir=$1

if [ ! -d "$src_dir" ]; then
  echo "'$src_dir' is not a directory"
  exit 1
fi

if [ $UID -ne 0 ]; then
  echo "$0 must be run as root"
  exit 1
fi

if [ -z "$CGI_DIR" ]; then
  CGI_DIR=/usr/lib/cgi-bin
fi
if [ -z "$ICON_DIR" ]; then
  ICON_DIR=/usr/share/apache2/icons
fi
if [ -z "$DOCUMENT_ROOT" ]; then
  DOCUMENT_ROOT=/var/www
fi

mkdir -v /etc/lmdb
mkdir -v /opt/lmdb
mkdir -vp $DOCUMENT_ROOT/lmdb/images
mkdir -v $CGI_DIR/lmdb
mkdir -v $ICON_DIR/lmdb

echo "$CGI_DIR" > /etc/lmdb/cgi_dir.txt
echo "$ICON_DIR" > /etc/lmdb/icon_dir.txt
echo "$DOCUMENT_ROOT" > /etc/lmdb/document_root.txt
echo "$src_dir" > /etc/lmdb/src_dir.txt

cp -v datafetcher.py /opt/lmdb/
cp -v db_handler.py /opt/lmdb/
cp -v db_syncd.py /opt/lmdb/
cp -v db_syncd_wrapper.sh /opt/lmdb/
cp -v dbctl.py /opt/lmdb/

ln -vs "$src_dir" $DOCUMENT_ROOT/lmdb/films

cp -v html/* $DOCUMENT_ROOT/lmdb/
cp -v images/no_poster.jpg $DOCUMENT_ROOT/lmdb/images/
cp -v images/icons/* $ICON_DIR/lmdb/
cp -v cgi-bin/* $CGI_DIR/lmdb/ 

touch /var/log/lmdb.log

adduser --system --no-create-home lmdb
chown lmdb /var/log/lmdb.log
chown lmdb $DOCUMENT_ROOT/lmdb/images

su -s /bin/bash postgres <<-EOF
  createuser --no-createdb --no-createrole --no-superuser lmdb
  createdb --owner=lmdb lmdb
EOF
 
su -s /bin/bash lmdb <<-EOF
  python initialize_db.py "$src_dir"
  psql "dbname=lmdb" -c 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "www-data"'
  python /opt/lmdb/db_syncd.py
  ( crontab -l 2>/dev/null; echo "@reboot /opt/lmdb/db_syncd_wrapper.sh" ) | crontab
EOF

