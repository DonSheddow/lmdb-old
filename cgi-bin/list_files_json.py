#!/usr/bin/python
import cgi
import json
import os
from re import sub
from urllib import quote, unquote

print "Content-Type: application/json"
print

form = cgi.FieldStorage()

with open("/etc/lmdb/document_root.txt") as f:
  DOCUMENT_ROOT = f.readline().strip()

path = DOCUMENT_ROOT+'/lmdb/films/'+sub(r'\.\.', '', unquote(form.getfirst('path')))

offset = len(DOCUMENT_ROOT+'/lmdb/films/')

if os.path.isfile(path):
  print json.dumps({path[offset:]: []})

else:
  output = {}
  for i in sorted(os.listdir(path)):
    i = path+'/'+i
    output[quote(i)[offset:]] = [ quote(j) for j in sorted(os.listdir(i)) ] if os.path.isdir(i) else []
  
  print json.dumps(output)
