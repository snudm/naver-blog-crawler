#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from glob import glob
import json


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def zipper(directory, ext='json'):
    filenames = glob('%s/*.%s' % (directory, ext))
    zipped = []
    for f in filenames:
        zipped.extend(read_json(f))
    return zipped

def zip_date(date, datadir):
    z = zipper('%s/%s' % (datadir, date.replace('-', '/')))
    with open('%s/%s.json' % (datadir, date), 'w') as f:
        json.dump(z, f)
