import psycopg2
import os

from urllib import urlretrieve

import datafetcher

conn = psycopg2.connect("dbname=lmdb")

def document_root():
  with open("/etc/lmdb/document_root.txt") as f:
    return f.readline().strip()

def fetch_images(url, film_id):
  img_path = document_root()+'/lmdb/images/'+str(film_id)+'.jpg'
  try:
    urlretrieve(url, img_path)
  except:
    os.symlink(document_root()+'/lmdb/images/no_poster.jpg', img_path)
  
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
  result = cur.fetchone()
  if not result:
    return
  film_id = result[0]
  
  poster = document_root()+'/lmdb/images/'+str(film_id)+'.jpg'
  if os.path.isfile(poster):
    os.remove(poster)
  
  cur.execute("DELETE FROM films WHERE id = %s", [film_id])
  conn.commit()
  cur.close()
  
  
def rename(pathname, new_pathname):
  cur = conn.cursor()
  cur.execute("SELECT id, imdbid FROM films WHERE pathname = %s", [pathname])
  result = cur.fetchone()
  film_id, current_imdbid = result if result else (None, None)
  
  new_imdbid = datafetcher.search(new_pathname)
  if new_imdbid == current_imdbid:
    cur.execute("UPDATE films SET pathname = %s WHERE id = %s", [new_pathname, film_id])
  else:
    delete(pathname)
    create(new_pathname, datafetcher.Data(new_imdbid))
  
  conn.commit()
  cur.close()
  
 
