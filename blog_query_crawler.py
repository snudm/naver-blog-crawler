#! /usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import timedelta
import os
import sys
import time
from urlparse import urlparse, parse_qs

from bs4 import BeautifulSoup
from lxml import etree, html
import paramiko
import requests

import blog_text_crawler as btc
from settings import DATADIR, ENCODING, REMOTE, SLEEP, QUERIES
import utils


listurl = 'http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=%s&term=&option.startDate=%s&option.endDate=%s&option.page.currentPage=%s&option.orderBy=date'
tagsurl = 'http://section.blog.naver.com/TagSearchAsync.nhn?variables=[%s]'
posturl = 'http://blog.naver.com/%s/%s'
mobileurl = 'http://m.blog.naver.com/%s/%s'


def requests_get(url):
    while 1:
        try:
            return requests.get(url)
        except:
            print('Pass error for %s' % url)
            return None


def get_nitems_for_query(query, sdate, edate):
    try:
        root = html.parse(listurl % (query, sdate, edate, 1))
        nitems = root.xpath('//p[@class="several_post"]/em/text()')[0]
        return int(nitems.strip(u'건'))
    except IOError:
        print('Pass IOError: (%s, %s)' % (query, sdate))
        return 0


def get_tags_for_items(item_keys):
    join_str = ','.join("{\"blogId\":\"%s\",\"logNo\":\"%s\"}" % (b, l) for b, l in item_keys)
    response = requests_get(tagsurl % join_str).json()
    return {(item['blogId'], unicode(item['logNo'])): item['tags'] for item in response}


def crawl_blog_post(blog_id, log_no, tags, written_time=None, verbose=True):

    def get_title(root):
        return root.xpath('//h3[@class="tit_h3"]/text()')[0].strip()

    def get_page_html(url):
        try:
            root = html.parse(url)
            elem = root.xpath('//div[@class="_postView"]')[0]
            html_ = etree.tostring(elem)
            return (BeautifulSoup(html_), get_title(root))
        except IOError:
            print ''
            return (None, None)

    if blog_id.startswith('http'):
        url = blog_id
    else:
        url = mobileurl % (blog_id, log_no)

    (doc, title)    = get_page_html(url)

    if doc:
        crawled_time    = utils.get_today_str()
        crawler_version = utils.get_version()
        url             = posturl % (blog_id, log_no)
        post_tags       = tags[(blog_id, log_no)]
        directory_seq   = None  # NOTE: No directory sequence given for query crawler

        post = btc.make_structure(blog_id, log_no, None, doc, crawled_time,
                crawler_version, title, written_time, url, post_tags, directory_seq)
        if not verbose:
            del post['directorySeq']
            del post['sympathyCount']
        return post

    else:
        print 'No doc in %s' % posturl
        return None


def get_dates(sdate, edate):
    sdt = utils.parse_datetime(sdate, form='%Y-%m-%d')
    edt = utils.parse_datetime(edate, form='%Y-%m-%d')

    delta = edt - sdt

    return [utils.format_datetime(sdt + timedelta(days=i), form='%Y-%m-%d')\
            for i in range(delta.days + 1)]


def crawl_blog_posts_for_query_per_date(query, date):

    def get_keys_from_page(query, date, pagenum):
        root = html.parse(listurl % (query, date, date, pagenum))
        items = root.xpath('//ul[@class="list_type_1 search_list"]')[0]

        blog_ids = items.xpath('./input[@name="blogId"]/@value')
        log_nos = items.xpath('./input[@name="logNo"]/@value')
        times = [utils.format_datetime(utils.parse_datetime(time))\
            for time in items.xpath('./li/div[@class="list_data"]/span[@class="date"]/text()')]

        return {(b, l): t for b, l, t in zip(blog_ids, log_nos, times)}


    # make directories
    subdir = '/'.join([DATADIR, query, date.split('-')[0]])
    utils.checkdir(subdir)
    if REMOTE:
        rsubdir = '/'.join([REMOTE['dir'], query, date.split('-')[0]])
        utils.rcheckdir(sftp, rsubdir)

    # check number of items
    try:
        nitems = get_nitems_for_query(query, date, date)
    except IndexError:
        print query, date, 'None'
        return

    # crawl items
    for pagenum in range(int(nitems/10.)):
        keys = get_keys_from_page(query, date, pagenum + 1)
        tags = get_tags_for_items(keys)
        for (blog_id, log_no), written_time in keys.items():
            try:
                info = crawl_blog_post(blog_id, log_no, tags, written_time, verbose=False)
                localpath = '%s/%s.json' % (subdir, log_no)
                utils.write_json(info, localpath)
                if REMOTE:
                    remotepath = '%s/%s.json' % (rsubdir, log_no)
                    sftp.put(localpath, remotepath)
            except IndexError:
                print Exception(\
                    'Crawl failed for http://blog.naver.com/%s/%s' % (blog_id, log_no))

            time.sleep(SLEEP)

    overwrite_queries(query, date)
    print query, date, nitems


def read_lines(filename):
    with open(filename, 'r') as f:
        return filter(None, f.read().decode(ENCODING).split('\n'))


def write_lines(lines, filename):
    with open(filename, 'w') as f:
        f.write(('\n'.join(lines)).encode(ENCODING))


def overwrite_queries(query, date):
    lines = read_lines(QUERIES)
    queries = [line.split()[2] for line in lines]
    index = queries.index(query)
    lines[index] = '%s %s' % (date, lines[index].split(' ', 1)[-1])
    write_lines(lines, QUERIES)


def open_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(REMOTE['ip'], username=REMOTE['id'], password=REMOTE['pw'])
    except:
        pass
    sftp = ssh.open_sftp()
    return ssh, sftp


def close_ssh(ssh, sftp):
    sftp.close()
    ssh.close()


if __name__=='__main__':

    trial = 1
    while 1:
        print 'Trial:', trial
        try:
            if REMOTE: ssh, sftp = open_ssh()

            qdset = []
            for line in [line.split()[:3] for line in read_lines(QUERIES)]:
                sdate, edate, query = line
                qdset.extend([query, d] for d in get_dates(sdate, edate))

            for q, d in qdset:
                crawl_blog_posts_for_query_per_date(q, d)

            if REMOTE: close_ssh(ssh, sftp)
        except Exception as e:
            print e
            trial += 1
    print 'Done.'
