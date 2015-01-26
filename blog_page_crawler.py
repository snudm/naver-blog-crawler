#! /usr/bin/python2.7
# -*-coding:utf-8-*-


import json
import os
import glob
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URLBASE = 'http://m.blog.naver.com/%s/%s'
REPLY_URLBASE = 'http://m.blog.naver.com/CommentList.nhn?blogId=%s&logNo=%s'

get_today = lambda : datetime.now()

def get_page(url):
    page = urllib2.urlopen(url)
    doc  = BeautifulSoup(page.read())
    return (doc, doc.find("div", {"class": "_postView"}))

def get_reply(url):
    page = urllib2.urlopen(url)
    doc  = BeautifulSoup(page.read())
    return doc.find_all("li", {"class": "persc"})

def make_structure(blog_id, log_no, raw, doc, replies, crawled_time, crawler_version, encoding='utf-8'):
    extract_crawlerTime  = lambda: get_today().strftime("%Y-%m-%d %H:%M")
    extract_category     = lambda doc: doc.find("a", {"class": "_categoryName"}).get_text().encode(encoding)
    extract_content_html = lambda doc: doc.find("div", {"id": "viewTypeSelector"})

    def extract_sympathycount(doc):
        if doc.find("em", {"id": "sympathyCount"}) == None:
            return 0
        else:
            return doc.find("em", {"id": "sympathyCount"}).get_text()

    def reply_json(reply):
        if reply.find("p") != None and reply.find("div", {"class":"dsc_id"}) != None:
            return {u"content": reply.find("p").get_text(),
                    u"date": reply.find("span").get_text().encode("utf"),
                    u"blogId": reply.find("div", {"class":"dsc_id"}).find("a")["href"].rsplit("blogId=", 1)[1]}

    def extract_reply(replies):
        all_replies = []
        for reply in range(0, len(replies)):
            tmp = reply_json(replies[reply])
            if tmp != None:
                retmp = replies[reply].find_all("ul", {"class":"lst_repl_sub"})
                re_replies = []
                for re in range(0, len(retmp)):
                    if reply_json(retmp[re]) != None:
                        re_replies.append(reply_json(retmp[re]))
                if re_replies != []:
                    tmp["reReply"] = re_replies
                all_replies.append(tmp)
        return all_replies

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
            u"categoryName": extract_category(doc),
            u"comments": extract_reply(replies),
            u"commentCrawledTime": extract_crawlerTime(),
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

def last_log_url(blog_id, log_no, directory_seq, basedir, seconddir = "logs"):
    targetpath = '%s/%s' % (basedir, seconddir)
    filename   = '%s/last_url_%02d.txt' % (targetpath, directory_seq)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)
    f = open(filename, 'w')
    url = 'http://m.blog.naver.com/%s/%s' % (blog_id, log_no)
    f.write(url)
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

def find_url_position(directory_seq, basedir, seconddir = "logs"):
    targetpath = '%s/%s/last_url_%02d.txt' % (basedir, seconddir, directory_seq)
    if not os.path.isfile(targetpath):
        url = []
    else:
        f   = open(targetpath, 'r')
        url = f.readline()
        f.close()
    return url

def web_crawl(blog_id, log_no, crawled_time, crawler_version, directory_seq, basedir):
    (raw, doc) = get_page(URLBASE % (blog_id, log_no))
    if doc != None:
        (reply_doc) = get_reply(REPLY_URLBASE % (blog_id, log_no))
        last_log_url(blog_id, log_no, directory_seq, basedir)
        blog = make_structure(blog_id, log_no, raw, doc, reply_doc, crawled_time, crawler_version)
        count_images(blog, directory_seq, basedir)
        make_json(blog, blog_id, log_no,directory_seq, basedir)
    else:
        error_log_url(blog_id, log_no, directory_seq, basedir)

def file_read(file):
   json_data = open(file)
   data = json.load(json_data)
   return data

def return_information(directory_seq, basedir, seconddir ="lists"):
    now = datetime.now()
    day = 0
    directory_seq = int(directory_seq)
    targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                         % (basedir, seconddir, directory_seq, now.year, now.month, now.day)
    flag = 0
    url = find_url_position(directory_seq, basedir)
    while(os.path.exists('./%s' % targetpath)):
        path = '%s/*.json' % targetpath
        files = glob.glob(path)
        for file in files:
            divs = file_read(file)
            for i, blog in enumerate(divs):
                this_url = 'http://m.blog.naver.com/%s/%s' % (divs[i]['blogId'], divs[i]['logNo'])
                if url == [] or flag == 1:
                    web_crawl(divs[i]['blogId'], divs[i]['logNo'],
                                    divs[i]['crawledTime'], divs[i]['crawlerVersion'], directory_seq, basedir)
                elif url == this_url:
                    web_crawl(divs[i]['blogId'], divs[i]['logNo'],
                                    divs[i]['crawledTime'], divs[i]['crawlerVersion'], directory_seq, basedir)
                    flag = 1
        day += 1
        today  = now.date() - timedelta(days=day)
        targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                         % (basedir, seconddir, directory_seq, today.year, today.month, today.day)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--category', required=True, dest='directory_seq',
                         help='assign target category to crawl')
    parser.add_argument('-p', '--path', dest='basedir',
                         help='assign data path')
    args = parser.parse_args()

    if not args.basedir:
        args.basedir = './data'

    return_information(args.directory_seq, args.basedir)

