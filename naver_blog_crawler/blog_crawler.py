#-*-coding:utf-8-*-


from bs4 import BeautifulSoup
import urllib2
import json

def crawl_page(url):
	page = urllib2.urlopen(url)
	doc = BeautifulSoup(page.read())
	images = doc.find_all("li", {"class":"add_img"})
	return images

def extract_image(image):
	img = image.find("div", {"class": "multi_img"}).img['src'].encode('utf-8')
	return img

def extract_title(image):
	title = image.find("a").get_text().encode('utf-8')
	return title

def extract_date(image):
	date = image.find("span",{"class": "date"}).get_text().encode('utf-8')
	return date

def extract_text(image):
	text = image.find("div", {"class":"list_content"}).get_text().encode('utf-8').strip()
	return text

def make_json_file(obj):
	jsonfile = json.dumps(obj, sort_keys = True, indent = 4, encoding = 'utf-8')
	return jsonfile

def write_file(jsonfile, i, p):
	f = open('data/FoodBlog_{0:02d}.json'.format(i+(p-1)*10), 'w')
	f.write(jsonfile)
	f.close()
	return 0

def make_structure(image):

	udate = extract_date(image)
	utitle = extract_title(image)
	utext = extract_text(image)
	uimg = extract_image(image)

	obj = {u"date": udate, 
		u"title": utitle, 
		u"text": utext, 
		u"img": uimg
	}

	return obj
		
def each_page_crawler(images, p):
	i = 1
	for image in images:
		obj = make_structure(image)
		jsonfile = make_json_file(obj)
		write_file(jsonfile, i, p)
		i = i + 1
	return 0

def total_page_crawler(page_need):
	for p in range(1, page_need+1):
		url = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?option.page.currentPage='+ str(p)+ '&option.templateKind=0&option.directorySeq=29&option.viewType=default&option.orderBy=quality&option.latestOnly=1'
		images = crawl_page(url)
		each_page_crawler(images, p)

	return 0

if __name__ == '__main__':
	page_need = input('How many blog pages you need?: ')
	total_page_crawler(page_need)

