#-*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime

TARGETS = ['book', 'movie', 'design', 'performance', \
           'music', 'drama', 'entertainer', 'cartoon', 'broadcasting', 'dailylife', \
           'infantmarriage', 'pet', 'goodwriting', 'fashion', 'interior', 'cooking', \
           'reviews', 'game', 'sport', 'picture', 'car', 'hobby', 'domestictravel', \
           'overseastrip', 'restaurant', 'IT', 'society', 'health', 'business', \
           'language', 'education']

URLBASE = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?'\
          'option.page.currentPage=%s&option.templateKind=0&option.directorySeq=29'\
          '&option.viewType=default&option.orderBy=quality&option.latestOnly=1'

def get_page(url):
    
    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    return doc.find_all("li", {"class":"add_img"})

def make_structure(div):

    def extract_url(div):
        return div.find("a")['href']

    def extract_writer(div):
        return div.find("div", {"class": "list_data"}).find("a").get_text().encode('utf-8')
    
    def extract_image(div):
        return div.find("div", {"class": "multi_img"}).img['src'].encode('utf-8')

    def extract_title(div):
        return div.find("a").get_text().encode('utf-8')

    def extract_date(div):
        return div.find("span", {"class": "date"}).get_text().encode('utf-8')

    def extract_text(div):
        return div.find("div", {"class":"list_content"}).get_text().encode('utf-8').strip()
    
    def extract_blogId(div):
        return div.find("input", {"class": "vBlogId"})['value']

    def extract_logNo(div):
        return div.find("input", {"class": "vLogNo"})['value']
    #TODO: tag extract error
    # def extract_tag(div):

    return {u"url": extract_url(div),
            u"writer": extract_writer(div),
            u"date": extract_date(div),
            u"title": extract_title(div),
            u"text": extract_text(div),
            u"img": extract_image(div),
            u"id": extract_blogId(div),
            u"logNo": extract_logNo(div)}

def make_json(objs, target, basedir='./data'):
    
   
    date = objs[0][0]["date"]
    print date
    
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]

    targetpath = '%s/%s/%s/%s/%s' % (basedir, target, year, month, day)
    now_time = datetime.today().hour

    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

    filename = '%s/%s-%s-%s-%s.json' % (targetpath, year, month, day, now_time)
    f = open(filename, 'a')
    jsonstr = json.dumps(objs, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()

def parse_page(divs, old_urls):
    
    objs = []
    flag = True

    for i, div in enumerate(divs):
        obj = make_structure(div)
        if obj['url'] in old_urls:
            flag = False
            break
        else:
            objs.append(obj)
    return (objs, flag)
    
def get_old_url(target, basedir='./data'):

    now_year = datetime.today().year
    now_month = datetime.today().month
    now_day = datetime.today().day
    now_hour = datetime.today().hour
      
    if now_hour >23:
        now_day = now_day - 1
        now_hour = 24

    targetpath = '%s/%s/%s/%02d/%02d' % (basedir, target, now_year, now_month, now_day)

    filename = '%s/%s-%02d-%02d-%02d.json' \
                    % (targetpath,now_year, now_month, now_day, now_hour-1)
    
    if os.path.isfile(filename):

        json_data = open(filename).read()
        data = json.load(json_data)
        old_urls = data['url']
    else:
        old_urls = []
    
    return old_urls

def crawl(target):
    # TODO: auto assign `page_need`
    new_items = []
    new_urls = []
    old_urls = get_old_url(target)
    pagenum = 1
    flag = True
    max_page = 100
    if old_urls == [] :
        max_page = 5
    while(flag == True and max_page > 1):
        
        divs = get_page(URLBASE % pagenum)
        objs, flag = parse_page(divs, old_urls)
        new_items.append(objs)
        pagenum += 1
        max_page -= 1

    make_json(new_items, target)

if __name__ == '__main__':
    import argparse

    targets =  ''.join('\n- %s' % t for t in TARGETS)

    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--target', required=True, dest='target',
                         help='assign target category to crawl%s' % targets)
    args = parser.parse_args()
    if args.target not in TARGETS:
        raise ValueError('Target values must be in%s' % targets)

    crawl(arg.target)
