#! /usr/bin/python2.7
# -*-coding:utf-8-*-


import json
import os
import glob
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URLBASE = 'http://m.blog.naver.com/%s/%s'

get_today = lambda : datetime.now()

def get_page(url):
    page = urllib2.urlopen(url)
    doc  = BeautifulSoup(page.read())
    return (doc, doc.find("div", {"class": "_postView"}))

def get_reply(url):
    page = urllib2.urlopen(url)
    doc  = BeautifulSoup(page.read())
    return doc.find_all("li", {"class": "persc"})

def make_structure(blog_id, log_no, raw, doc, crawled_time, crawler_version,
                                     title, written_time, url, tags, encoding='utf-8'):
    extract_crawlerTime  = lambda: get_today().strftime("%Y-%m-%d %H:%M")
    extract_category     = lambda doc: doc.find("a", {"class": "_categoryName"}).get_text().encode(encoding)
    extract_content_html = lambda doc: doc.find("div", {"id": "viewTypeSelector"})

    def extract_sympathycount(doc):
        if doc.find("em", {"id": "sympathyCount"}) == None:
            return 0
        else:
            return doc.find("em", {"id": "sympathyCount"}).get_text()

    def extract_images(htmls = extract_content_html(doc)):
        image_urls = []
        images = htmls.find_all("span", {"class":"_img _inl fx"})
        for i, image in enumerate(images):
            tmp = images[i]['thumburl'] + 'w2'
            image_urls.append(tmp)
        return image_urls

    return {u"blogId": blog_id,
            u"logNo": log_no,
            u"contentHtml": [str(extract_content_html(doc))],
            u"content": [extract_content_html(doc).get_text().encode(encoding)],
            u"crawledTime": crawled_time,
            u"crawlerVersion": crawler_version,
            u"title": title,
            u"writtenTime": written_time,
            u"url": url,
            u"tags": tags,
            u"categoryName": extract_category(doc),
            u"sympathyCount": extract_sympathycount(doc),
            u"images": extract_images()}

def make_json(blog, blog_id, log_no, directory_seq, basedir, seconddir = "texts"):
    PATH = get_today().date().isoformat().replace("-", "/")
    targetpath = '%s/%s/%02d/%s' % (basedir, seconddir, directory_seq, PATH)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)
    filename = '%s/%s-%s.json' % (targetpath, blog_id, log_no)
    f        = open(filename, 'w')
    jsonstr  = json.dumps(blog, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()

def count_images(blog, directory_seq, basedir, seconddir = "logs"):
    targetpath = '%s/%s' % (basedir, seconddir)
    filename = '%s/count_images_%02d.txt' % (targetpath, directory_seq)
    f = open(filename, 'a')
    f.write(str(len(blog["images"]))+'\n')
    f.close()

def error_log_url(blog_id, log_no, directory_seq, basedir, seconddir = "logs"):
    now = datetime.now()
    targetpath = '%s/%s' % (basedir, seconddir)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)
    filename = '%s/error_url_%s-%02d-%02d.txt' % (targetpath, now.year, now.month, now.day)
    f   = open(filename, 'a')
    url = '%s, http://m.blog.naver.com/%s/%s, access denied\n' % (directory_seq, blog_id, log_no)
    f.write(url)
    f.close()

def web_crawl(blog_id, log_no, crawled_time, crawler_version, title, 
                        written_time, url, tags, directory_seq, basedir):
    (raw, doc) = get_page(URLBASE % (blog_id, log_no))
    if doc != None:
        blog = make_structure(blog_id, log_no, raw, doc, crawled_time,
                        crawler_version, title, written_time, url, tags)
        count_images(blog, directory_seq, basedir)
        make_json(blog, blog_id, log_no,directory_seq, basedir)
    else:
        error_log_url(blog_id, log_no, directory_seq, basedir)

def file_read(filename):
   json_data = open(filename)
   data = json.load(json_data)
   return data

def return_information(directory_seq, basedir, date, seconddir ="lists", thirddir="texts"):
    directory_seq = int(directory_seq)
    targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                         % (basedir, seconddir, directory_seq,\
                            int(date[0:4]), int(date[5:7]), int(date[8:10]))
   
    filenames = glob.glob('%s/*.json' % targetpath)
    for filename in reversed(filenames):
        items = file_read(filename)
        for i, blog in enumerate(items):
            check_targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                            % (basedir, thirddir, directory_seq,\
                               int(date[0:4]), int(date[5:7]), int(date[8:10]))
            check_filename = '%s-%s.json' % (items[i]['blogId'], items[i]['logNo'])
            if not os.path.isfile('%s/%s' % (check_targetpath, check_filename)):
                web_crawl(items[i]['blogId'],
                          items[i]['logNo'],
                          items[i]['crawledTime'],
                          items[i]['crawlerVersion'],
                          items[i]['title'],
                          items[i]['writtenTime'],
                          items[i]['url'],
                          items[i]['tags'],
                          directory_seq,
                          basedir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--category', required=True, dest='directory_seq',
                         help='assign target category to crawl')
    parser.add_argument('-p', '--path', dest='basedir',
                         help='assign data path')
    parser.add_argument('-d', '--date', dest='date',
                         help='assign date to crawl')
    args = parser.parse_args()

    if not args.basedir:
        args.basedir = './data'

    return_information(args.directory_seq, args.basedir, args.date)

