#!/usr/bin/python
import cgi
import os
from re import sub
from urllib import quote, unquote

with open("/etc/lmdb/document_root.txt") as f:
  DOCUMENT_ROOT = f.readline().strip()

offset = len(DOCUMENT_ROOT+'/lmdb/films/')

def print_files(path):
  if os.path.isfile(path):
    print quote(path[offset:])
    return
  
  for name in sorted(os.listdir(path)):
    print_files(path+'/'+name)

print "Content-Type: application/json"
print

form = cgi.FieldStorage()

path = DOCUMENT_ROOT+'/lmdb/films/'+sub(r'\.\.', '', unquote(form.getfirst('path')))

print_files(path)
