#!/usr/bin/env python
import pyinotify
import logging
import os

from time import sleep
from thread import start_new_thread

import db_handler

logging.basicConfig(filename='/var/log/lmdb.log', format='[%(asctime)s] %(message)s', level=logging.INFO, datefmt='%c')

def rename(src, target):
  src = os.path.basename(src)
  target = os.path.basename(target)
  
  logging.info('Renaming %s ...', src)
  db_handler.rename(src, target)
  logging.info('... to %s', target)

def delete(path):
  path = os.path.basename(path)
  
  logging.info('Deleting %s ...', path)
  db_handler.delete(path)
  logging.info('... deleted %s', path)
  
def create(path):
  path = os.path.basename(path)
  
  logging.info('Creating %s ...', path)
  db_handler.create(path)
  logging.info('... created %s', path)

# Deletes files that are moved out of the directory
# Deletes the film unless it is handled by process_MOVED_TO in <10ms
def timeout_delete(path):
  sleep(0.01)
  if path in move_cache:
    delete(path)
    move_cache.remove(path)

move_cache = []

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM

class EventHandler(pyinotify.ProcessEvent):
  
  def process_IN_MOVED_FROM(self, event):
    move_cache.append(event.pathname)
    start_new_thread(timeout_delete, (event.pathname,))
  
  def process_IN_MOVED_TO(self, event):
    if hasattr(event, 'src_pathname'):
      move_cache.remove(event.src_pathname)
      rename(event.src_pathname, event.pathname)
    else:
      create(event.pathname)
  
  def process_IN_CREATE(self, event):
    create(event.pathname)
  
  def process_IN_DELETE(self, event):
    delete(event.pathname)
    


handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)

with open("/etc/lmdb/src_dir.txt") as f:
  src_dir = f.readline().strip()
wdd = wm.add_watch(src_dir, mask)

notifier.loop(daemonize=True, stdout='/tmp/lmdb.out', stderr='/tmp/lmdb.out', pid_file='/tmp/lmdb.pid')
