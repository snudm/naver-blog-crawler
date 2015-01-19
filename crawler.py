#-*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta


URLBASE = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?'\
          'option.page.currentPage=%s&option.templateKind=0&option.directorySeq=%s&'\
          'option.viewType=default&option.orderBy=date&option.latestOnly=%s'


def get_page(url):

    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    tmp_doc = doc.find("ul", {"class": "list_type_1"})
    return tmp_doc.find_all("li")


def make_structure(div, crawler_version, encoding='utf-8'):

    sanitize = lambda s: s.get_text().encode(encoding).strip()

    extract_blog_id = lambda d: d.find("input", {"class": "vBlogId"})['value']
    extract_date   = lambda d: sanitize(d.find("span", {"class": "date"})).replace(".", "-")
    extract_log_no  = lambda d: d.find("input", {"class": "vLogNo"})['value']
    extract_text   = lambda d: sanitize(d.find("div", {"class":"list_content"}))
    extract_title  = lambda d: sanitize(d.find("a"))
    extract_url    = lambda d: d.find("a")['href']
    extract_writer = lambda d: sanitize(d.find("div", {"class": "list_data"}).find("a"))
    extract_crawlerTime = lambda: datetime.now().strftime("%Y-%m-%d %H:%M")

    def extract_image(div):
        d = div.find("div", {"class": "multi_img"})
        if not d:
            return []
        else:
            return d.img['src'].encode(encoding)

    return {u"blogId": extract_blog_id(div),
            u"blogName": extract_writer(div),
            u"content": extract_text(div),
            u"crawledTime": extract_crawlerTime(),
            u"crawlerVersion": crawler_version,
            u"images": [{u"url":extract_image(div)}],
            u"logNo": extract_log_no(div),
            u"title": extract_title(div),
            u"writtenTime": extract_date(div),
            u"url": extract_url(div)}


def make_json(objs, category_id, version, basedir='./data'):

    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    hour = datetime.today().hour
    minute = datetime.today().minute
    sec = datetime.today().second

    targetpath = '%s/%02d/%s/%02d/%02d' % (basedir, category_id, year, month, day)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

    filename = '%s/%s-%02d-%02d-%02d%02d%02d.json' \
                    % (targetpath, year, month, day, hour, minute, sec)

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


def get_old_url(category_id, basedir='./data', FlagDir=1):

    now_year = datetime.today().year
    now_month = datetime.today().month
    now_day = datetime.today().day

    while (FlagDir<10):

        targetpath = '%s/%02d/%s/%02d/%02d'\
                % (basedir, category_id, now_year, now_month, now_day)
        if os.path.exists('./%s' % targetpath):
            filename = max(os.listdir('./%s' % targetpath))
            PATH = '%s/%s' % (targetpath, filename)
            json_data = open(PATH).read()
            data = json.loads(json_data)
            old_urls =[]
            for i, blog in enumerate(data):
                old_urls.extend([data[i]['url']])
            break
        else:
            yesterday = datetime.now().date() - timedelta(days=FlagDir)
            FlagDir += 1
        now_year = yesterday.year
        now_month = yesterday.month
        now_day = yesterday.day

    if FlagDir == 10:
            old_urls = []

    return old_urls


def crawl(category_id, version, ispopular=1, debug=False):
    if debug:
        max_page = 3
    else:
        max_page = 100

    category_id = int(category_id)
    new_items = []
    new_urls = []
    old_urls = get_old_url(category_id)
    pagenum = 1
    flag = True
    while(flag == True and max_page >= 1):
        divs = get_page(URLBASE % (pagenum, category_id, ispopular))
        objs, flag = parse_page(divs, old_urls, version)
        objs_tags = extract_tag(objs)
        new_items.extend(objs_tags)
        pagenum += 1
        max_page -= 1
    if new_items != [] :
        make_json(new_items, category_id, version)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--category', required=True, dest='category_id',
                         help='assign target category to crawl')
    parser.add_argument('-v', '--version', required=True, dest='version',
                         help='notice version of crawler')
    parser.add_argument('-t', '--type', dest='ispopular',
                         help='notice whether to crawl popular posts (1) or all posts (0)')
    args = parser.parse_args()

    crawl(args.category_id, args.version, args.ispopular, debug=True)
