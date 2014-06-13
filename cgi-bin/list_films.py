#!/usr/bin/env python
import psycopg2
import json
import cgi, cgitb
cgitb.enable()

print "Content-Type: application/json"
print

conn = psycopg2.connect("dbname=lmdb")
form = cgi.FieldStorage()

cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", ["films"])
columns = [ i[0] for i in cur.fetchall() ]

query = "SELECT %s FROM films WHERE title IS NOT NULL" % ",".join(columns)

year_lowerbound = form.getfirst('year_lowerbound', 0)
year_upperbound = form.getfirst('year_upperbound', 9999)

query += " AND (start_year<=%s AND (%s<=end_year OR end_year IS NULL))"
values = [year_upperbound, year_lowerbound]

#cur.execute("SELECT unnest(enum_range(NULL::type))")
#types = [ i[0] for i in cur.fetchall() ]
types = ['movie', 'series']

type_ = form.getfirst('type')

if type_ in types:
  query += " AND (type = %s)"
  values.append(type_)




ordering = form.getfirst('order_by', 'title')

if ordering in columns:
  query += " ORDER BY %s" % ordering
else:
  query += " ORDER BY title"

cur.execute(query, values)

output = json.dumps([ dict(zip(columns, row)) for row in cur.fetchall() ])
print output
