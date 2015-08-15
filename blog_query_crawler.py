#! /usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import timedelta
import sys
from urlparse import urlparse, parse_qs

if 'threading' in sys.modules:
    raise Exception('threading module loaded before patching!')
from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
from bs4 import BeautifulSoup
from lxml import etree, html
import requests

import blog_text_crawler as btc
import utils


ENCODING = 'utf-8'

listurl = 'http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=%s&term=&option.startDate=%s&option.endDate=%s&option.page.currentPage=%s&option.orderBy=date'
tagsurl = 'http://section.blog.naver.com/TagSearchAsync.nhn?variables=[%s]'
posturl = 'http://blog.naver.com/%s/%s'
mobileurl = 'http://m.blog.naver.com/%s/%s'


def get_nitems_for_query(query, sdate, edate):
    root = html.parse(listurl % (query, sdate, edate, 1))
    try:
        nitems = root.xpath('//p[@class="several_post"]/em/text()')[0]
        return int(nitems.strip(u'건'))
    except IndexError:
        return 0


def get_items_from_page(query, date, pagenum):
    root = html.parse(listurl % (query, date, date, pagenum))
    return root.xpath('//ul[@class="list_type_1 search_list"]/li')


def get_tags_for_items(item_keys):
    join_str = ','.join("{\"blogId\":\"%s\",\"logNo\":\"%s\"}" % (b, l) for b, l in item_keys)
    response = requests.get(tagsurl % join_str).json()
    return {(item['blogId'], unicode(item['logNo'])): item['tags'] for item in response}


def get_keys_for_item(item):
    proxy = item.xpath('./h5/a/@href')[0]
    parts = urlparse(proxy)
    if parts.netloc=='blog.naver.com':
        blog_id = parts.path.strip('/')
        log_no = parse_qs(parts.query)['logNo'][0]
        return (blog_id, log_no)
    else:
        try:
            proxy = html.parse(proxy).xpath('//frame/@src')[0]
            parts = urlparse(proxy)
            return tuple(parts.path.split('/')[1:])
        except (IOError, IndexError):
            return tuple([proxy, None])


def get_time_for_item(item):
    time = item.xpath('./div[@class="list_data"]/span[@class="date"]/text()')[0]
    return utils.format_datetime(utils.parse_datetime(time))


def crawl_blog_post(blog_id, log_no, tags, written_time=None, verbose=True):

    def get_page_html(url):
        resp = requests.get(url, headers={'referer': 'http://search.naver.com'})
        root = html.fromstring(resp.text)
        elem = root.xpath('//div[@class="_postView"]')[0]
        html_ = etree.tostring(elem)
        return (None, BeautifulSoup(html_))

    def get_title(root):
        try:
            return root.xpath('//h3[@class="tit_h3"]/text()')[0].strip()
        except IndexError:
            return None

    url = mobileurl % (blog_id, log_no)
    root = html.parse(url)

    (raw, doc)      = get_page_html(url)
    crawled_time    = utils.get_today_str()
    crawler_version = utils.get_version()
    title           = get_title(root)
    url             = posturl % (blog_id, log_no)
    post_tags       = tags[(blog_id, log_no)]
    directory_seq   = None  # NOTE: No directory sequence given for query crawler

    if doc:
        post = btc.make_structure(blog_id, log_no, raw, doc, crawled_time,
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


def crawl_blog_posts_for_query_per_date(*args):
    query, date = args[0]

    subdir = '/'.join([DATADIR, query, date.split('-')[0]])
    utils.checkdir(subdir)

    nitems = get_nitems_for_query(query, date, date)
    for pagenum in range(int(nitems/10.)):
        items = get_items_from_page(query, date, pagenum + 1)
        keys = {get_keys_for_item(item): get_time_for_item(item) for item in items}
        tags = get_tags_for_items(keys)
        for (blog_id, log_no), written_time in keys.items():
            try:
                info = crawl_blog_post(blog_id, log_no, tags, written_time, verbose=False)
                utils.write_json(info, '%s/%s.json' % (subdir, log_no))
            except IndexError:
                print Exception(\
                        'Crawl failed for http://blog.naver.com/%s/%s' % (blog_id, log_no))

    print query, date, nitems


def print_expected_counts(queries):
    for line in queries:
        query = line.split()[0]
        print query, get_nitems_for_query(query, sdate, edate)


if __name__=='__main__':
    DATADIR = './tmp'                           # change me
    sdate, edate = '2010-01-01', '2015-08-01'   # change me

    with open('queries.txt', 'r') as f:
        queries = [line.split()[0] for line in f.read().decode(ENCODING).split('\n')[:-1]]
    dates = get_dates(sdate, edate)
    qdset = [[q, d] for q in queries for d in dates]

    print('Get expected document counts')
    print_expected_counts(queries)

    print('Start crawling:')
    pool = Pool(20)
    pool.map(crawl_blog_posts_for_query_per_date, qdset)
