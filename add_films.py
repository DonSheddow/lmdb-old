import sys
import os

import db_handler

if len(sys.argv) < 2:
  sys.exit(1)

src_dir = sys.argv[1]

for f in os.listdir(src_dir):
  db_handler.create(f)
