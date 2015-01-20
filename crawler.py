#! /usr/bin/python2.7
# -*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime, timedelta


URLBASE = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?'\
          'option.page.currentPage=%s&option.templateKind=0&option.directorySeq=%s&'\
          'option.viewType=default&option.orderBy=date&option.latestOnly=%s'


get_today = lambda : datetime.now()


def get_page(url):

    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    tmp_doc = doc.find("ul", {"class": "list_type_1"})
    return tmp_doc.find_all("li")


def make_structure(div, crawler_version, encoding='utf-8'):

    sanitize = lambda s: s.get_text().encode(encoding).strip()

    extract_blog_id = lambda d: d.find("input", {"class": "vBlogId"})['value']
    extract_date    = lambda d: sanitize(d.find("span", {"class": "date"})).replace(".", "-")
    extract_log_no  = lambda d: d.find("input", {"class": "vLogNo"})['value']
    extract_text    = lambda d: sanitize(d.find("div", {"class":"list_content"}))
    extract_title   = lambda d: sanitize(d.find("a"))
    extract_url     = lambda d: d.find("a")['href']
    extract_writer  = lambda d: sanitize(d.find("div", {"class": "list_data"}).find("a"))
    extract_crawlerTime = lambda: get_today().strftime("%Y-%m-%d %H:%M")

    def extract_image(div):
        d = div.find("div", {"class": "multi_img"})
        if not d:
            return []
        else:
            url = d.img['src'].encode(encoding)
            if url.endswith("?type=s88"):
                return [url.rsplit("?", 1)[0]]
            else:
                return [url]

    return {u"blogId": extract_blog_id(div),
            u"blogName": extract_writer(div),
            u"content": extract_text(div),
            u"crawledTime": extract_crawlerTime(),
            u"crawlerVersion": crawler_version,
            u"images": extract_image(div),
            u"logNo": extract_log_no(div),
            u"title": extract_title(div),
            u"writtenTime": extract_date(div),
            u"url": extract_url(div)}


def make_json(objs, directory_seq, version, basedir):

    today  = get_today()

    PATH = get_today().date().isoformat().replace("-", "/")
    targetpath = '%s/%02d/%s/' % (basedir, directory_seq, PATH)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

    filename = '%s/%s-%02d%02d%02d.json' \
                    % (targetpath,
                        get_today().date().isoformat(),
                        today.hour, today.minute, today.second)

    f = open(filename, 'w')
    jsonstr = json.dumps(objs, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()


def parse_page(divs, old_urls, version):

    objs = []
    flag = True
    for i, div in enumerate(divs):
        obj = make_structure(div, version)
        if obj['url'] in old_urls:
            flag = False
            break
        else:
            objs.append(obj)
    return (objs, flag)


def extract_tag(divs):

    ids = []
    for obj in divs:
        ids.append((obj['blogId'], obj['logNo']))

    join_str = ','.join("{\"blogId\":\"%s\",\"logNo\":\"%s\"}" \
                    % (b, l) for b, l in ids)

    tags_url = 'http://section.blog.naver.com/TagSearchAsync.nhn?variables=[%s]' % join_str
    response = urllib2.urlopen(tags_url)
    html = json.loads(response.read())

    for i, obj in enumerate(html):
        divs[i]["tags"] = obj['tags']
    return divs


def get_old_url(directory_seq, basedir, flag_dir=1):

    today     = get_today()
    now_year  = today.year
    now_month = today.month
    now_day   = today.day

    while (flag_dir<10):

        targetpath = '%s/%02d/%s/%02d/%02d'\
                % (basedir, directory_seq, now_year, now_month, now_day)
        if os.path.exists(targetpath):
            filename = max(os.listdir(targetpath))
            PATH = '%s/%s' % (targetpath, filename)
            json_data = open(PATH).read()
            data = json.loads(json_data)
            old_urls =[]
            for i, blog in enumerate(data):
                old_urls.extend([data[i]['url']])
            break
        else:
            yesterday = datetime.now().date() - timedelta(days=flag_dir)
            flag_dir += 1
        now_year = yesterday.year
        now_month = yesterday.month
        now_day = yesterday.day

    if flag_dir == 10:
        old_urls = []
    return old_urls


def crawl(directory_seq, basedir, version, latest_only=1, debug=False):

    if debug:
        max_page = 3
    else:
        max_page = 100

    directory_seq = int(directory_seq)
    new_items = []
    new_urls = []
    old_urls = get_old_url(directory_seq, basedir)
    pagenum = 1
    flag = True
    while(flag == True and max_page >= 1):
        divs = get_page(URLBASE % (pagenum, directory_seq, latest_only))
        objs, flag = parse_page(divs, old_urls, version)
        objs_tags = extract_tag(objs)
        new_items.extend(objs_tags)
        pagenum += 1
        max_page -= 1
    if new_items != [] :
        make_json(new_items, directory_seq, version, basedir)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--category', required=True, dest='directory_seq',
                         help='assign target category to crawl')
    parser.add_argument('-v', '--version', dest='version',
                         help='notice version of crawler')
    parser.add_argument('-l', '--latest-only', dest='latest_only',
                         help='option to crawl popular posts (1) or all posts (0)')
    parser.add_argument('-t', '--type', dest='type',
                         help='option to crawl popular posts (popular) or all posts (all)')
    parser.add_argument('-p', '--path', dest='basedir',
                         help='assign data path')
    args = parser.parse_args()

    if not args.basedir:
        args.basedir = './data'

    if not args.version:
        with open('version.cfg', 'r') as f:
            args.version = f.read().strip()

    if args.type:
        if args.type=='all':
            args.lastest_only = 0
        elif args.type=='popular':
            args.latest_only = 1
        else:
            raise Exception('Wrong type of argument for -t, --type')

    crawl(args.directory_seq, args.basedir, args.version, args.latest_only, debug=False)