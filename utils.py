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
        print('Created %s' % directory)


def rcheckdir(sftp, remotedir):
    try:
        sftp.chdir(remotedir)
    except IOError:
        dirname, basename = os.path.split(remotedir.rstrip('/'))
        rcheckdir(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)


def file_read(filename):
   json_data = open(filename)
   data = json.load(json_data)
   return data


def get_version():
    with open('version.cfg', 'r') as f:
        return f.read().strip()


def parse_datetime(string, form='%Y.%m.%d. %H:%M'):
    return datetime.strptime(string, form)


def format_datetime(dt, form='%Y-%m-%d %H:%M'):
    return dt.strftime(form)


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
