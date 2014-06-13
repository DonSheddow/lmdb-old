import psycopg2
import argparse

from re import search
from os.path import basename

import db_handler
import datafetcher

conn = psycopg2.connect("dbname=lmdb")

def reinitialize_film(pathname, imdb_id, tmdb_id=None):
  
  data = datafetcher.Data(imdb_id, tmdb_id)
  
  db_handler.delete(pathname)
  db_handler.create(pathname, data)
  

def set_imdbid(pathname, imdb_url):
  
  imdb_id = search(r'/?(tt\d{7})/?', imdb_url).group(1)
  
  db_handler.delete(pathname)
  db_handler.create(pathname, imdb_id)

def update_info(pathname):
  cur = conn.cursor()
  cur.execute("SELECT id, imdbid FROM films WHERE pathname = %s", [pathname])
  film_id, imdb_id = cur.fetchone()
  
  if imdb_id:
    data = datafetcher.Data(key)
    info = data.info()
    query = "UPDATE films SET (%s) = (%s) WHERE id = %%s" % (', '.join(info.keys()), ', '.join('%s' for i in info))
    cur.execute(query, info.values()+[film_id])
  
  conn.commit()
  cur.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--initialize", action="store_true")
  group.add_argument("--update", action="store_true")
  group.add_argument("--set-imdb", "--set-IMDb", dest="imdb_url", help="From imdbID or a url containing imdbID")
  group.add_argument("--set-tmdb", "--set-TMDb", dest="tmdb_id")
  parser.add_argument("path")
  args = parser.parse_args()
  
  pathname = basename(args.path)
  
  if args.initialize:
    db_handler.initialize(args.path)
  
  elif args.update:
    update_info(pathname)
  
  elif args.imdb_url:
    imdb_id = search(r'/?(tt\d{7})/?', args.imdb_url).group(1)
    reinitialize_film(pathname, imdb_id)
  
  else:
    cur = conn.cursor()
    cur.execute("SELECT imdbid FROM films WHERE pathname = %s", [pathname])
    imdb_id = cur.fetchone()[0]
    cur.close()
    
    reinitialize_film(pathname, imdb_id, args.tmdb_id)
