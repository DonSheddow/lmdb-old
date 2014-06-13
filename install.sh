#!/bin/bash

# Prerequisites:
#
# apache2
#   libapache2-mod-python
#
# psql
#   postgres role $USER with createdb priviliges
#
# python
#   psycopg2
#   pyinotify
#   PIL (Python Image Library)
# 

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <src_dir>"
  exit 1
fi

src_dir="$1"

createdb lmdb
mkdir /var/www/lmdb

sudo ln -vs "$src_dir" /var/www/films
sudo mkdir -v /var/www/images
sudo chmod a+w /var/www/images

sudo cp -v images/no_poster.jpg /var/www/images/
sudo cp -v images/icons/* /usr/share/apache2/icons/

sudo cp -v html/* /var/www/lmdb/
sudo cp -v cgi-bin/* /usr/lib/cgi-bin/

sudo touch /var/log/lmdb.log
sudo chmod -v a+w /var/log/lmdb.log

python -c "import db_handler; db_handler.initialize('${src_dir//\'/\\\'}')"

p="$(pwd)/db_syncd.py"
python "$p"
( crontab -l 2>/dev/null | grep -Fv "$p" ; echo "@reboot python '$p'" ) | crontab

