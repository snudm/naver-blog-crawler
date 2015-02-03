#! /usr/bin/python2.7
# -*-coding:utf-8-*-

import json
import os
import glob
import urllib2

from datetime import datetime, timedelta

from utils import checkdir, file_read, get_today, get_version

def target_path(directory_seq, date, basedir,seconddir):

	targetpath ='%s/%s/%02d/%s/%02d/%02d' % (basedir, seconddir, directory_seq,\
												int(date[0:4]), int(date[5:7]), int(date[8:10]))
	return targetpath


def make_json(directory_seq, cnt_texts_blog, cnt_image, cnt_lists_blog, cnt_time_blog, cnt_comments):
	
	if cnt_lists_blog == 0:
		percentage = 0
	else: 
		percentage = float(cnt_texts_blog)/float(cnt_lists_blog)*100

	cnt = {u"directorySeq": directory_seq,
	   	   u"countTextsBlog": cnt_texts_blog,
	   	   u"countImage": cnt_image, 
	   	   u"countListsBlog": cnt_lists_blog,
	   	   u"successText": '{0:.02f}%'.format(percentage), 
	   	   u"timeBlog": cnt_time_blog,
	   	   u"countComment": cnt_comments}
	return cnt


def count_blog_by_directory(directory_seq, date, basedir, seconddir='texts'):
	#basedir: /var/data/naver-blog/
	targetpath = target_path(directory_seq, date, basedir,seconddir)
	filenames = glob.glob('%s/*.json' % targetpath)
	cnt_image = 0
	for i, filename in enumerate(filenames):
		items = file_read(filename)
		cnt_image = cnt_image + len(items['images'])
	return (len(filenames), cnt_image)


def original_count_blog_by_directory(directory_seq, date, basedir, seconddir='lists'):
	
	targetpath = target_path(directory_seq, date, basedir,seconddir)
	filenames = glob.glob('%s/*.json' % targetpath)
	cnt_lists_blog = 0
	for i, filename in enumerate(filenames):
		items = file_read(filename)
		cnt_lists_blog =  cnt_lists_blog + len(items)
	return cnt_lists_blog


def original_count_blog_by_time(directory_seq, date, basedir, seconddir='lists'):

	time_cnt = {}
	for d in range(0, 2):
		tmp_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=d)
		tmp_date = tmp_date.isoformat()
		
		targetpath = target_path(directory_seq, tmp_date, basedir,seconddir)
		filenames = glob.glob('%s/*.json' % targetpath)
		for i, filename in enumerate(filenames):
			items = file_read(filename)
			for j, item in enumerate(items):
				written_time = item['writtenTime']
				if int(written_time[8:10]) == int(date[8:10]):
					key = int(written_time[11:13])
					if key in time_cnt.keys():
						time_cnt[key] += 1 
					else:
						time_cnt[key] = 0
	return [time_cnt]
			

def original_count_comment(directory_seq, date, basedir, seconddir='comments'):

	targetpath = target_path(directory_seq, date, basedir,seconddir)
	filenames = glob.glob('%s/*.json' % targetpath)
	cnt_comments = 0
	for i, filename in enumerate(filenames):
		items = file_read(filename)
		cnt_comments = cnt_comments	+ len(items['comments'])
	return cnt_comments


def write_json(static_blog, date, basedir, seconddir='statistics'):
	
    PATH = '%s-%02d-%02d' % (int(date[0:4]), int(date[5:7]), int(date[8:10]))
    targetpath = '%s/%s' % (basedir, seconddir)
    checkdir(targetpath)
    filename = '%s/%s.json' % (targetpath, PATH)
    f        = open(filename, 'w')
    jsonstr  = json.dumps(static_blog, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()


def statistics_blog(date, basedir):

	static_blog = []
	for directory_seq in range(5, 36):
		cnt_texts_blog, cnt_image = count_blog_by_directory(directory_seq, date, basedir)
	  	cnt_lists_blog  = original_count_blog_by_directory(directory_seq, date, basedir)
	  	cnt_time_blog   = original_count_blog_by_time(directory_seq, date, basedir)
	  	cnt_comments    = original_count_comment(directory_seq, date, basedir)
	  	jstr = make_json(directory_seq, cnt_texts_blog, cnt_image, cnt_lists_blog, cnt_time_blog, cnt_comments)
	  	static_blog.append(jstr)
	write_json(static_blog, date, basedir)

if __name__ == '__main__':
	start_day = '2015-01-20'
	end_day = '2015-02-02'
	gap = (datetime.strptime(end_day, '%Y-%m-%d')\
				- datetime.strptime(start_day, '%Y-%m-%d')).days

	for day in range(0, gap+1):

		tmp_date = datetime.strptime(start_day, '%Y-%m-%d') + timedelta(days=day)
		tmp_date = tmp_date.isoformat()
		statistics_blog(tmp_date[:10], '/home/web/public_html/data/naver-blog')
		print tmp_date[]
