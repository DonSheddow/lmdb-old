#!/bin/bash

if [ $UID -ne 0 ]; then
  echo "This script must be run as root"
  exit 1
fi

CGI_DIR=$(cat /etc/lmdb/cgi_dir.txt)
ICON_DIR=$(cat /etc/lmdb/icon_dir.txt)
DOCUMENT_ROOT=$(cat /etc/lmdb/document_root.txt)

rm -rv $CGI_DIR/lmdb
rm -rv $ICON_DIR/lmdb
rm -rv $DOCUMENT_ROOT/lmdb

rm -rv /etc/lmdb
rm -rv /opt/lmdb

( crontab -l 2>/dev/null | grep -Fv "/opt/lmdb/db_syncd_wrapper.sh" ) | crontab
kill "$(cat /tmp/lmdb.pid)"

rm -v /var/log/lmdb.log
rm -v /tmp/lmdb.out
rm -v /tmp/lmdb.pid

su postgres <<-EOF
  dropdb lmdb
  dropuser lmdb
EOF

deluser lmdb
