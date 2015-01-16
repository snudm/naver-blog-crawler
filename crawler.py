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
          'option.page.currentPage=%s&option.templateKind=0&option.directorySeq=%s&'\
          'option.viewType=default&option.orderBy=date&option.latestOnly=1'

def get_page(url):
    
    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    tmp_doc = doc.find("ul", {"class": "list_type_1"})
    return tmp_doc.find_all("li")

def make_structure(div):

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
   
    return {u"url": extract_url(div),
            u"writer": extract_writer(div),
            u"datetime": extract_date(div),
            u"title": extract_title(div),
            u"content": extract_text(div),
            u"images": [{u"url":extract_image(div)}],
            u"provider": extract_blogId(div),
            u"aid": extract_logNo(div)}

def make_json(objs, target, basedir='./data'):
       
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    hour = datetime.today().hour
    minute = datetime.today().minute
    sec = datetime.today().second

    targetpath = '%s/%s/%s/%02d/%02d' % (basedir, target, year, month, day)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)
    
    filename = '%s/%s-%02d-%02d-%02d%02d%02d.json' \
                    % (targetpath, year, month, day, hour, minute, sec)

    f = open(filename, 'w')
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

def extract_tag(divs):
        
    blog_ids, log_nos = [], []
    
    for obj in divs:
        blog_ids.append(obj['provider'])
        log_nos.append(obj['aid'])
   
    join_str = ','.join("{\"blogId\":\"%s\",\"logNo\":\"%s\"}" \
                    % (b, l) for b, l in zip(blog_ids, log_nos))
       
    tags_url = 'http://section.blog.naver.com/TagSearchAsync.nhn?variables=[%s]' % join_str
    response = urllib2.urlopen(tags_url)
    html = json.loads(response.read())

    for i, obj in enumerate(html):
        obj["tags"] = obj['tags'] 
    return divs
        
def get_old_url(target, basedir='./data'):

    now_year = datetime.today().year
    now_month = datetime.today().month
    now_day = datetime.today().day
    now_hour = datetime.today().hour
      
    if now_hour >23:
        now_day = now_day - 1
        now_hour = 24

    targetpath = '%s/%s/%s/%02d/%02d' % (basedir, target, now_year, now_month, now_day)
    if os.path.exists('./%s' % targetpath):
        filename = max(os.listdir('./%s' % targetpath))
        PATH = '%s/%s' % (targetpath, filename)
        json_data = open(PATH).read()
        data = json.loads(json_data)
        old_urls =[]
        for i, blog in enumerate(data):
            old_urls.extend([data[i]['url']])
    else:
        old_urls = []

    return old_urls

def crawl(sectionID):
    # TODO: auto assign `page_need`
    new_items = []
    new_urls = []
    target = extract_sectionID(sectionID)
    old_urls = get_old_url(target)
    pagenum = 1
    flag = True
    max_page = 100
    if old_urls == [] :
        max_page = 5
    while(flag == True and max_page >= 1):
        
        divs = get_page(URLBASE % (pagenum, sectionID))
        objs, flag = parse_page(divs, old_urls)
        objs_tags = extract_tag(objs)
        new_items.extend(objs_tags)
        pagenum += 1
        max_page -= 1

    make_json(new_items, target)

def read_section_information():
    f = open("section_information.txt", "r")
    lines = f.readlines()
    tg = []
    secID = []
    for line in lines:
        tg.append(line.split(",")[0].replace("'", ""))
        secID.append(int(line.split(",")[1]))
    return zip(tg, secID)

def extract_sectionID(sectionID):
    secList = read_section_information()
    for i in range(0, len(secList)):
        if secList[i][1] == sectionID:
            idx = i 
    return secList[idx][0]

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
