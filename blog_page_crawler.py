#! /usr/bin/python2.7
# -*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime, timedelta


URLBASE = 'http://m.blog.naver.com/%s/%s'
REPLY_URLBASE = 'http://m.blog.naver.com/CommentList.nhn?blogId=%s&logNo=%s'

# blog_id = 30139621
# log_no = 220246406613

blog_id = 'sung011403'
log_no = 220246731488
directory_seq = 29

get_today = lambda : datetime.now()

def get_page(url):

    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    return (doc, doc.find("div", {"class": "_postView"}))
  
def get_reply(url):

    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    return doc.find_all("li", {"class": "persc"})

def make_structure(raw, doc, replies, encoding='utf-8'):

    # sanitize = lambda s: s.get_text().encode(encoding).strip()
    extract_crawlerTime   = lambda: get_today().strftime("%Y-%m-%d %H:%M")
    extract_category      = lambda doc: doc.find("a", {"class": "_categoryName"}).get_text().encode(encoding)
    extract_content_html  = lambda doc: doc.find("div", {"class": "post_ct"})
    extract_sympathycount = lambda doc: doc.find("em", {"id": "sympathyCount"}).get_text()
    reply_json = lambda reply: {u"content": reply.find("p").get_text(),
                                u"date": reply.find("span").get_text().encode("utf"),
                                u"blogId": reply.find("div", {"class":"dsc_id"}).find("a")["href"].rsplit("blogId=", 1)[1]}
    def extract_reply(replies):
        all_replies = []
        for reply in range(0, len(replies)):
            tmp = reply_json(replies[reply])
            retmp = replies[reply].find_all("ul", {"class":"lst_repl_sub"})
            re_replies = []
            for re in range(0, len(retmp)):
                re_replies.append(reply_json(retmp[re]))
            tmp["reReply"] = re_replies 
            all_replies.append(tmp)
        return all_replies

    return {u"blogId": blog_id,
            u"logNo": log_no,
            u"htmlContent": [str(extract_content_html(doc))],
            u"content": [extract_content_html(doc).get_text().encode(encoding)],
            # u"crawledTime": extract_crawlerTime(),
            # u"crawlerVersion": crawler_version,
            u"category": extract_category(doc),
            u"comments": extract_reply(replies),
            u"commentCrawledTime": extract_crawlerTime()}

def web_crawl():
    (raw, doc) = get_page(URLBASE % (blog_id, log_no))
    (reply_doc) = get_reply(REPLY_URLBASE % (blog_id, log_no))
    blog = make_structure(raw, doc, reply_doc)
    make_json(blog, blog_id, log_no)

def make_json(blog, blog_id, log_no, basedir="./blogs"):

    PATH = get_today().date().isoformat().replace("-", "/")
    targetpath = '%s/%02d/%s' % (basedir, directory_seq, PATH)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

    filename = '%s/%s-%s.json' % (targetpath,blog_id, log_no)
    f = open(filename, 'w')
    jsonstr = json.dumps(blog, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()

if __name__ == '__main__':

    web_crawl()