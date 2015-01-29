#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from datetime import datetime
import os

get_today = lambda : datetime.now()

def checkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def file_read(filename):
   json_data = open(filename)
   data = json.load(json_data)
   return data
