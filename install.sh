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

restore_data=false
for i in "$@"; do
  if [ "$i" == "--restore-data" ]; then
    restore_data=true
  else
    src_dir="$i"
  fi
done

if [ -z "$src_dir" ]; then
  echo "Usage: $0 [--restore-data] <src_dir>"
  exit 1
fi

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
  psql -f initialize_db.sql 
  psql -c 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "www-data"'
  
  if [ "$restore_data" == "true" ]; then
    psql -f /tmp/lmdb_data.sql
    tar xzf /tmp/lmdb_images.tar.gz -C "$DOCUMENT_ROOT/lmdb/images/"
  else
    python add_films.py "$src_dir"
  fi
  
  python /opt/lmdb/db_syncd.py
  ( crontab -l 2>/dev/null | grep -Fv "/opt/lmdb/db_syncd_wrapper.sh"; echo "@reboot /opt/lmdb/db_syncd_wrapper.sh" ) | crontab
EOF
