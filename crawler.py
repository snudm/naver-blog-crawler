#-*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup


URLBASE = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?option.page.currentPage=%s&option.templateKind=0&option.directorySeq=29&option.viewType=default&option.orderBy=quality&option.latestOnly=1'
TARGETS = ['food', 'tour', 'technology']

def crawl_page(url):
    page = urllib2.urlopen(url)
    doc = BeautifulSoup(page.read())
    return doc.find_all("li", {"class":"add_img"})

def make_structure(image):
    def extract_image(image):
        return image.find("div", {"class": "multi_img"})\
                    .img['src'].encode('utf-8')

    def extract_title(image):
        return image.find("a")\
                    .get_text().encode('utf-8')

    def extract_date(image):
        return image.find("span",{"class": "date"})\
                    .get_text().encode('utf-8')

    def extract_text(image):
        return image.find("div", {"class":"list_content"})\
                    .get_text().encode('utf-8').strip()

    return {u"date": extract_date(image),
            u"title": extract_title(image),
            u"text": extract_text(image),
            u"img": extract_image(image)}

def write_obj_to_file(obj, i, p, target):
    # f = open('data/food/FoodBlog_{0:02d}.json'.format(i+(p-1)*10), 'w')
    date = obj["date"]
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]

    newpath = r'C:/Users/Misuk/Dropbox/DMLAB/2014 intern/Crawler/naver_blog_crawler/data/' +target
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    f = open('data/food/%s-%s-%s.json' % (year, month, day), 'a')
    jsonstr = json.dumps(obj, sort_keys=True, indent=4, encoding='utf-8')
    jsonstr = jsonstr + '\n'
    f.write(jsonstr)
    # f.write('\n')
    f.close()

def total_page_crawler(target):
    # TODO: auto assign `page_need`
    page_need = 10
    for p in range(1, page_need+1):
        images = crawl_page(URLBASE % p)
        for i, image in enumerate(images):
            obj = make_structure(image)
            write_obj_to_file(obj, i+1, p, target)


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

    total_page_crawler(args.target)
