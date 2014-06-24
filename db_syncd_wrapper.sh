#!/bin/bash
while [ -z "$(pgrep postgres)" ]; do
  sleep 0.5
done
sleep 1

python /opt/lmdb/db_syncd.py
