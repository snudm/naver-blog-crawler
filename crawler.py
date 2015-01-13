#-*-coding:utf-8-*-


import json
import os
import urllib2

from bs4 import BeautifulSoup


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
    def extract_image(div):
        return div.find("div", {"class": "multi_img"}).img['src'].encode('utf-8')

    def extract_title(div):
        return div.find("a").get_text().encode('utf-8')

    def extract_date(div):
        return div.find("span", {"class": "date"}).get_text().encode('utf-8')

    def extract_text(div):
        return div.find("div", {"class":"list_content"}).get_text().encode('utf-8').strip()

    return {u"date": extract_date(div),
            u"title": extract_title(div),
            u"text": extract_text(div),
            u"img": extract_image(div)}

def write_obj_to_file(obj, i, p, target, basedir='./data'):
    date = obj["date"]
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]

    targetpath = '%s/%s' % (basedir, target)

    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

    f = open('%s/%s-%s-%s.json' % (targetpath, year, month, day), 'a')
    jsonstr = json.dumps(obj, sort_keys=True, indent=4, encoding='utf-8')
    jsonstr = jsonstr + '\n'
    f.write(jsonstr)
    f.close()

def crawl(target):
    # TODO: auto assign `page_need`
    page_need = 10
    for p in range(1, page_need+1):
        divs = get_page(URLBASE % p)
        for i, div in enumerate(divs):
            obj = make_structure(div)
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

    crawl(args.target)
