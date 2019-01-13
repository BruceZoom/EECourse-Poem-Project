# coding = utf-8

from selenium import webdriver
# from bs4 import BeautifulSoup
# import urllib2
# import urlparse
# import json
import codecs
import sys
import os

def save_page(driver, url, filename):
	driver.get(url)
	html = driver.execute_script("return document.documentElement.outerHTML")
	with codecs.open(filename, 'w', encoding='utf-8') as fout:
		fout.write(html)

if __name__ == '__main__':
	f = 1
	t = (4531586 + 199) // 200
	if len(sys.argv) > 1:
		f = int(sys.argv[1])
	if len(sys.argv) > 2:
		t = int(sys.argv[2])
	s = 1
	if f > t:
		s = -1

	if not os.path.exists("veer/fengguang/"):
		os.mkdirs("veer/fengguang/")
	driver = webdriver.Firefox()
	for i in range(f, t, s):
		print 'current page:', i
		url = "https://www.veer.com/query/photo?phrase=%E9%A3%8E%E5%85%89&page={}&perpage=200".format(i)
		filename = "veer/fengguang/page-{}.html".format(i)
		save_page(driver, url, filename)
