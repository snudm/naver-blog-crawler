#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import os

get_today = lambda : datetime.now()
get_today_str = lambda: get_today().strftime('%Y-%m-%d %H:%M')


def checkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def file_read(filename):
   json_data = open(filename)
   data = json.load(json_data)
   return data


def get_version():
    with open('version.cfg', 'r') as f:
        return f.read().strip()


def parse_datetime(string):
    return datetime.strptime(string, '%Y.%m.%d. %H:%M')


def format_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M')


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
