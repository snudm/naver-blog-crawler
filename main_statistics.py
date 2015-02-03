#! /usr/bin/python2.7
# -*-coding:utf-8-*-
import json
import os
import glob
import csv

from datetime import datetime, timedelta

from utils import checkdir, file_read, get_today, get_version

if __name__ == '__main__':
	
	num_directory_seq = 31
	basedir = '/home/web/public_html/data/naver-blog'
	seconddir = 'statistics'
	targetpath = '%s/%s' % (basedir, seconddir)
	filenames = glob.glob('%s/*.json' % targetpath)
	cnt_files = len(filenames)
	table = [ [ 0 for i in range(cnt_files) ] for j in range(num_directory_seq + 2) ]
	for i, filename in enumerate(filenames):
		items = file_read(filename)
		print filename
		table[0][i] = filename.rsplit("statistics/", 1)[1].rsplit(".", 1)[0]
		for directory_seq in range(len(items)):
			table[directory_seq+1][i] = items[directory_seq]['countTextsBlog']
			table[num_directory_seq+1][i] = table[num_directory_seq+1][i] + table[directory_seq+1][i]
	csvfile = open('test_file.csv', 'w')
	wr = csv.writer(csvfile, dialect='excel')
	[wr.writerow(r) for r in table]
