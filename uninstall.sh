#!/bin/bash

sudo rm /var/www/films
sudo rm -r /var/www/images

for i in images/icons/*; do
  sudo rm "/usr/share/apache2/icons/${i##*/}"
done

for i in html/*; do
  sudo rm "/var/www/lmdb/${i##*/}"
done

for i in cgi-bin/*; do
  sudo rm "/usr/lib/cgi-bin/${i##*/}"
done

p="$(pwd)/db_syncd.py"
( crontab -l 2>/dev/null | grep -Fv "$p" ) | crontab

kill "$(cat /tmp/lmdb.pid)"

sudo rm /var/log/lmdb.log
sudo rm /tmp/lmdb.pid
sudo rm /tmp/lmdb.out

dropdb lmdb
