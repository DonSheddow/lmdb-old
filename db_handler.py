import psycopg2
import re
import os

from PIL import Image
from urllib import urlretrieve

import datafetcher

conn = psycopg2.connect("dbname=lmdb")


def fetch_images(url, film_id):
  poster = '/var/www/images/'+str(film_id)+'.jpg'
  thumbnail = '/var/www/images/'+str(film_id)+'-thumbnail.jpg'
  
  try:
    urlretrieve(url, poster)
  except:
    os.symlink('/var/www/images/no_poster.jpg', poster)
  
  img = Image.open(poster)
  img.thumbnail((80,80), Image.ANTIALIAS)
  img.save(thumbnail)

def add_actors(actors, film_id):
  cur = conn.cursor()
  for actor, character, order in actors:
    cur.execute("SELECT id FROM people WHERE name = %s", [actor])
    result = cur.fetchone()
    if result:
      actor_id = result[0]
    else:
      cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING id", [actor])
      actor_id = cur.fetchone()[0]
    
    cur.execute("INSERT INTO performances (film_id, actor_id, character, order_of_appearance) VALUES (%s, %s, %s, %s)", [film_id, actor_id, character, order])
  conn.commit()
  cur.close()

def add_crew(crewmembers, film_id):
  cur = conn.cursor()
  for crewmember, department in crewmembers:
    cur.execute("SELECT id FROM people WHERE name = %s", [crewmember])
    result = cur.fetchone()
    if result:
      person_id = result[0]
    else:
      cur.execute("INSERT INTO people (name) VALUES (%s) RETURNING id", [crewmember])
      person_id = cur.fetchone()[0]
    
    cur.execute("INSERT INTO crew (film_id, crewmember_id, department) VALUES (%s, %s, %s)", [film_id, person_id, department])
  
  conn.commit()
  cur.close()


def create(pathname, data=None):
  cur = conn.cursor()
  
  if not data:
    imdb_id = datafetcher.search(pathname)
    data = datafetcher.Data(imdb_id) if imdb_id else None
  
  if data:
    info = data.info()
    query = "INSERT INTO films (%s, pathname) VALUES (%s, %%s) RETURNING id" % (', '.join(info.keys()), ', '.join('%s' for i in info))
    cur.execute(query, info.values()+[pathname])
    
    film_id = cur.fetchone()[0]
    
    for genre in data.genres():
      cur.execute("INSERT INTO genres (film_id, genre) VALUES (%s, %s)", [film_id, genre])
    
    conn.commit()
    cur.close()
    
    add_actors(data.actors(), film_id)
    add_crew(data.crew(), film_id)
    
    fetch_images(data.poster_url(), film_id)
  
  else:
    cur.execute("INSERT INTO films (pathname) VALUES (%s)", [pathname])
    conn.commit()
    cur.close()
  


def delete(pathname):
  cur = conn.cursor()
  cur.execute("SELECT id FROM films WHERE pathname = %s", [pathname])
  film_id = cur.fetchone()[0]
  
  poster = '/var/www/images/'+str(film_id)+'.jpg'
  if os.path.isfile(poster):
    os.remove(poster)
  
  thumbnail = '/var/www/images/'+str(film_id)+'-thumbnail.jpg'
  if os.path.isfile(thumbnail):
    os.remove(thumbnail)
  
  cur.execute("DELETE FROM films WHERE id = %s", [film_id])
  conn.commit()
  cur.close()
  
  
def rename(pathname, new_pathname):
  cur = conn.cursor()
  cur.execute("SELECT id, imdbid FROM films WHERE pathname = %s", [pathname])
  film_id, current_imdbid = cur.fetchone()
  
  new_imdbid = datafetcher.search(new_pathname)
  if new_imdbid == current_imdbid:
    cur.execute("UPDATE films SET pathname = %s WHERE id = %s", [new_pathname, film_id])
  else:
    delete(pathname)
    create(new_pathname, datafetcher.Data(new_imdbid))
  
  conn.commit()
  cur.close()
  
 
def initialize(src_dir):
  src_dir = os.path.abspath(src_dir)
  
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
    create(f)


