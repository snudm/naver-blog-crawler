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

def make_structure(div, crawler_version):

    def extract_url(div):
        return div.find("a")['href']

    def extract_writer(div):
        return div.find("div", {"class": "list_data"}).find("a").get_text().encode('utf-8')
    
    def extract_image(div):
        if div.find("div", {"class": "multi_img"}) is None:
            return []
        else: 
            return div.find("div", {"class": "multi_img"}).img['src'].encode('utf-8')

    def extract_title(div):
        return div.find("a").get_text().encode('utf-8')

    def extract_date(div):
        return div.find("span", {"class": "date"}).get_text().encode('utf-8').replace(".", "-")

    def extract_text(div):
        return div.find("div", {"class":"list_content"}).get_text().encode('utf-8').strip()
    
    def extract_blogId(div):
        return div.find("input", {"class": "vBlogId"})['value']

    def extract_logNo(div):
        return div.find("input", {"class": "vLogNo"})['value']
    def extract_crawlerTime():
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    return {u"url": extract_url(div),
            u"blogName": extract_writer(div),
            u"writtenTime": extract_date(div),
            u"title": extract_title(div),
            u"content": extract_text(div),
            u"images": [{u"url":extract_image(div)}],
            u"blogId": extract_blogId(div),
            u"logNo": extract_logNo(div),
            u"crawledTime": extract_crawlerTime(),
            u"crawlerVersion": crawler_version}

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
        
    blog_ids, log_nos = [], []
    
    for obj in divs:
        blog_ids.append(obj['blogId'])
        log_nos.append(obj['logNo'])
   
    join_str = ','.join("{\"blogId\":\"%s\",\"logNo\":\"%s\"}" \
                    % (b, l) for b, l in zip(blog_ids, log_nos))
       
    tags_url = 'http://section.blog.naver.com/TagSearchAsync.nhn?variables=[%s]' % join_str
    response = urllib2.urlopen(tags_url)
    html = json.loads(response.read())

    for i, obj in enumerate(html):
        divs[i]["tags"] = obj['tags'] 
    return divs
        
def get_old_url(category_id, basedir='./data'):

    now_year = datetime.today().year
    now_month = datetime.today().month
    now_day = datetime.today().day

    FlagDir = 1
    while (FlagDir<10):
        
        targetpath = '%s/%02d/%s/%02d/%02d' % (basedir, category_id, now_year, now_month, now_day)
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

def crawl(category_id, version, ispopular):
    # TODO: auto assign `page_need`
    new_items = []
    new_urls = []
    old_urls = get_old_url(category_id)
    pagenum = 1
    flag = True
    max_page = 100
    if old_urls == [] :
        max_page = 100
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
    # import argparse

    # targets =  ''.join('\n- %s' % t for t in TARGETS)

    # parser = argparse.ArgumentParser(description='Get input parameters.',
    #                     formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument('-t', '--target', required=True, dest='target',
    #                      help='assign target category to crawl%s' % targets)
    # args = parser.parse_args()
    # if args.target not in TARGETS:
    #     raise ValueError('Target values must be in%s' % targets)
   
    # crawl(arg.target)
    version = 0.1
    ispopular = 1
    for category_id in range(5, 36):
        crawl(category_id, version, ispopular) # version number add