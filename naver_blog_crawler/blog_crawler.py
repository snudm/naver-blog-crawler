#-*-coding:utf-8-*-


from bs4 import BeautifulSoup
import urllib2
import json


URLBASE = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?option.page.currentPage=%s&option.templateKind=0&option.directorySeq=29&option.viewType=default&option.orderBy=quality&option.latestOnly=1'

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

def write_obj_to_file(obj, i, p):
	f = open('data/FoodBlog_{0:02d}.json'.format(i+(p-1)*10), 'w')
	jsonstr = json.dumps(obj, sort_keys=True, indent=4, encoding='utf-8')
	f.write(jsonstr)
	f.close()

def total_page_crawler(page_need):
	for p in range(1, page_need+1):
		images = crawl_page(URLBASE % p)
		for i, image in enumerate(images):
			obj = make_structure(image)
			write_obj_to_file(obj, i+1, p)


if __name__ == '__main__':
	page_need = input('How many blog pages you need?: ')
	total_page_crawler(page_need)
