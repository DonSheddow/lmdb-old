import psycopg2
import sys
import os

import db_handler

if len(sys.argv) < 2:
  print "Usage: %s <src_dir>" % sys.argv[0]
  sys.exit(1)

src_dir = sys.argv[1]

conn = psycopg2.connect("dbname=lmdb")
cur = conn.cursor()
cur.execute("CREATE TYPE type AS ENUM(%s, %s)", ['movie', 'series'])
cur.execute("""CREATE TABLE films (pathname varchar(256) UNIQUE NOT NULL,
                                   id SERIAL PRIMARY KEY,
                                   title text,
                                   start_year smallint, 
                                   end_year smallint,
                                   plot text,
                                   imdbid char(9),
                                   type type,
                                   awards text,
                                   metascore smallint,
                                   imdbrating real,
                                   tomatometer smallint,
                                   tomatoconsensus text,
                                   tomatousermeter smallint,
                                   tomatoimage text
                                  )
            """)

cur.execute("""CREATE TABLE genres (
                                    film_id integer REFERENCES films ON DELETE CASCADE,
                                    genre text
                                   )
            """)

cur.execute("""CREATE TABLE people (
                                    id SERIAL PRIMARY KEY,
                                    name text UNIQUE NOT NULL
                                   )
            """)

cur.execute("""CREATE TABLE performances (
                                          film_id integer REFERENCES films ON DELETE CASCADE,
                                          actor_id integer REFERENCES people,
                                          character text,
                                          order_of_appearance integer
                                         )
            """)

cur.execute("""CREATE TABLE crew (
                                  film_id integer REFERENCES films ON DELETE CASCADE,
                                  crewmember_id integer REFERENCES people,
                                  department text
                                 )
            """)

conn.commit()
cur.close()

for f in os.listdir(src_dir):
  db_handler.create(f)

