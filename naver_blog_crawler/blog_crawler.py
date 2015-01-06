#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import urllib2
import json



i=0
img_url = {}
title = {}
date = {}
text_sep={} 


for j in range(1,6):

	url = 'http://section.blog.naver.com/sub/PostListByDirectory.nhn?option.page.currentPage='+ str(j)+ '&option.templateKind=0&option.directorySeq=29&option.viewType=default&option.orderBy=quality&option.latestOnly=1'
	page = urllib2.urlopen(url)
	doc = BeautifulSoup(page.read())
	images = doc.find_all("li", {"class":"add_img"})
	


	## file writing 

	for image in images:
		img_url[i] = image.find("div", {"class": "multi_img"}).img['src'].encode('utf-8')
		title[i] = image.find("a").get_text().encode('utf-8')
		# title[i] = image.contents[1].get_text().encode('utf-8').strip()	
		date[i] = image.find("span",{"class": "date"}).get_text().encode('utf-8')
		text_sep[i]=image.find("div", {"class":"list_content"}).get_text().encode('utf-8').strip()
		print title[i]
		# f = open('../data/FoodBlog_{0:02d}.txt'.format(i+(j-1)*10), 'w')
		# f.write(date[i]+'\n')
		# f.write(title[i]+'\n')
		# f.write(text_sep[i]+'\n')
		# f.write(img_url[i])
		# f.close()
		
		## json tranform
		obj={u"date": date[i], 
		u"title": title[i], 
		u"text": text_sep[i], 
		u"img": img_url[i]}
		jsonfile=json.dumps(obj, sort_keys=True, indent=4, encoding='utf-8')
		f = open('../data/FoodBlog_{0:02d}.json'.format(i+(j-1)*10), 'w')
		f.write(jsonfile)
		f.close()
		
		i = i+1
		break

	# if i==5:
	# 	break
	
	# print title_lists.contents[3].img['src'].encode('utf-8') # console print encode error,ex) picture name= Korean
# print img_url

	
""" 
	save json file   
	obj = {u"url": title_lists.contents[3].img['src'].encode('utf-8'), u"text":title_lists.get_text().encode('utf-8').replace('\n\n','\n')}
	print (json.dumps(obj))
	print str(obj)

"""

