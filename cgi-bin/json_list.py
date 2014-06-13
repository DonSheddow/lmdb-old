#!/usr/bin/python
import cgi
import json
import os
from re import sub
from urllib import quote, unquote

print "Content-Type: application/json"
print

form = cgi.FieldStorage()

path = '/var/www/films/'+sub(r'\.\.', '', unquote(form.getfirst('path')))

offset = len('/var/www/films/')

output = {}
for i in sorted(os.listdir(path)):
  i = path+'/'+i
  output[quote(i)[offset:]] = [ quote(j) for j in sorted(os.listdir(i)) ] if os.path.isdir(i) else []

print json.dumps(output)
