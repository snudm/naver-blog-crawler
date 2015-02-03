#! /usr/bin/python2.7
# -*-coding:utf-8-*-
import json
import os
import glob

from datetime import datetime, timedelta

from blog_statistic import statistics_blog

if __name__ == '__main__':
	start_day = '2015-01-20'
	end_day = '2015-02-02'
	gap = (datetime.strptime(end_day, '%Y-%m-%d')\
				- datetime.strptime(start_day, '%Y-%m-%d')).days

	for day in range(0, gap+1):

		tmp_date = datetime.strptime(start_day, '%Y-%m-%d') + timedelta(days=day)
		tmp_date = tmp_date.isoformat()
		statistics_blog(tmp_date, './')