#! /usr/bin/python2.7
# -*-coding:utf-8-*-

import json
import os
import glob
from datetime import datetime, timedelta

DAYS = 7

def make_json(week_urls, basedir, directory_seq):
   jsonstr = {u"urls": week_urls}
   today  = datetime.now()
   path = today.date().isoformat().replace("-", "/")
   targetpath = '%s/%02d/%s/' % (basedir, directory_seq, path)
   if not os.path.exists(targetpath):
      os.makedirs(targetpath)
   filename = '%s/%s_urls.json' % (targetpath, today.date().isoformat())
   f = open(filename, 'w')
   jsonstr = json.dumps(jsonstr, sort_keys=True, indent=4, encoding='utf-8')
   f.write(jsonstr)
   f.close()

def file_read(file):
   json_data = open(file)
   data = json.load(json_data)
   return data

def stack_urls(data, week_urls):
   for i, blog in enumerate(data):
      week_urls.append(data[i]['url'])
   return week_urls

def gather_week_urls(basedir ="./lists", directory_seq = 29, week_urls=[]):
   now = datetime.now()
   for day in range(0, DAYS):
      today  = now.date() - timedelta(days=day)
      targetpath = '%s/%02d/%s/%02d/%02d'\
            % (basedir, directory_seq, today.year, today.month, today.day)
      if os.path.exists('./%s' % targetpath):
         path = '%s/*.json' % targetpath
         files = glob.glob(path)
         for file in files:
            week_urls = stack_urls(file_read(file), week_urls)
      else:
         break
   make_json(week_urls, basedir, directory_seq)

if __name__ == '__main__':

   gather_week_urls()