#!/bin/bash
while [ -z "$(pgrep postgres)" ]; do
  sleep 0.5
done

python db_syncd.py
