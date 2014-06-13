import json
import re
import logging

from urllib2 import urlopen, quote, HTTPError
from string import digits
from os.path import splitext

API_KEY = '75235e7ed08c7a34f01e80ed1ef4eeb3'

OMDB_KEYS = ['Awards', 'Metascore', 'imdbRating', 'tomatoMeter', 'tomatoConsensus', 'tomatoUserMeter', 'tomatoImage', 'Title', 'Plot', 'imdbID', 'Type']

def genres():
  f = urlopen('http://api.themoviedb.org/3/genre/list?api_key=' + API_KEY)
  genres = json.loads(f.read())['genres']
  return [ genre['name'] for genre in genres ]


def search(pathname):
  title = splitext(pathname)[0]
  regex = r'\((\d{4})\)$'
  m = re.search(regex, title)
  if m:
    year = m.group(1)
    title = re.sub(r' ?' + regex, '', title) # Strip year off of title
  else:
    year = ''

  f = urlopen('http://omdbapi.com/?s=%s&y=%s' % (quote(title), year))
  result = json.loads(f.read())
  
  try:
    result = result['Search']
  except KeyError:
    return None
  
  for i in result:
    if i['Type'] in ['movie', 'series']:
      return i['imdbID']
  
  return None



def _fetchjson(url):
  try:
    f = urlopen(url)
  except HTTPError as e:
    if e.code == 503:
      logging.info("Service is currently unavailable. There will now be a short intermission.")
      print "Service is currently unavailable. There will now be a short intermission."
      sleep(10)
      logging.info("Retrying...")
      print "Retrying..."
      return _fetchjson(url)
    else:
      raise e
  
  return json.loads(f.read())


def _tmdbid(imdb_id, title, type_):
  url = 'http://api.themoviedb.org/3/find/%s?external_source=imdb_id&api_key=%s' % (imdb_id, API_KEY)
  result = _fetchjson(url)['%s_results' % type_]
  try:
    tmdb_id = result[0]['id']
  except IndexError:
    logging.warning("Couldn't find TMDb entry for IMDB id '%s'! Attempting to look up title '%s'... ", imdb_id, title)
    url = 'http://api.themoviedb.org/3/search/%s?query=%s&api_key=%s' % (type_, quote(title), API_KEY)
    f = urlopen(url)
    tmdb_id = json.loads(f.read())['results'][0]['id']
  
  return tmdb_id

def _replace(old, new, iterable):
  return (new if i == old else i for i in iterable)

class Data(object):
  
  def __init__(self, imdb_id, tmdb_id=None):
    omdb = _fetchjson('http://omdbapi.com/?i=%s&tomatoes=true' % imdb_id)
    self._omdb = dict(zip(omdb.keys(), _replace('N/A', None, omdb.values())))
    
    t = 'movie' if self._omdb['Type'] == 'movie' else 'tv'
    
    if not tmdb_id:
      tmdb_id = _tmdbid(imdb_id, self._omdb['Title'], t)
    
    self._tmdb = _fetchjson('http://api.themoviedb.org/3/%s/%s?api_key=%s' % (t, tmdb_id, API_KEY))
    
    self._credits = _fetchjson('http://api.themoviedb.org/3/%s/%s/credits?api_key=%s' % (t, tmdb_id, API_KEY))
    
  
  def info(self):
    out = dict((key.lower(), self._omdb[key]) for key in OMDB_KEYS)
    year = self._omdb['Year']
    out['start_year'] = int(year[:4])
    out['end_year'] = int(year[-4:]) if year[-1] in digits else None
    
    if not out['plot']:
      out['plot'] = self._tmdb['overview']
    
    return out
  
  def genres(self):
    tmdb_genres = set(genre['name'] for genre in self._tmdb['genres'])
    omdb_genres = set(_replace('Sci-Fi', 'Science Fiction', self._omdb['Genre'].split(', ')))
    return tmdb_genres.union(omdb_genres)
  
  def actors(self):
    return [ (i['name'], i['character'], i['order']) for i in self._credits['cast'] ]
  
  def crew(self):
    crew = set((i['name'], i['department']) for i in self._credits['crew'])
    if self._omdb['Type'] == 'series':
      created_by = set((i['name'], 'Directing') for i in self._tmdb['created_by'])
    else:
      created_by = set()
    
    return crew.union(created_by)
  
  def poster_url(self):
    return self._omdb['Poster']
  
