# coding = utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib2
import urlparse
import json
import codecs
import sys
import os

def extract_page(filename, img_list):
	with codecs.open(filename, 'r', encoding='utf-8') as fin:
		html = fin.read()
		soup = BeautifulSoup(html)
	for imgsec in soup.findAll('a', {'class': 'search_result_asset_link'}):
		try:
			item = {
				'source': imgsec['href'],
				'imgurl': imgsec.img['src'],
			}
			try:
				item['alt'] = imgsec.img['alt']
			except:
				item['alt'] = ''
			img_list.append(item)
		except Exception, e:
			print 'failed', e,message

if __name__ == '__main__':
	directory = 'veer/fengguang/'
	img_list = []
	files = os.listdir(directory)
	cnt = 0
	for filename in files:
		print 'current file: ' + filename, 'progress:', cnt, '', len(files)
		extract_page(directory+filename, img_list)
		cnt += 1
		if cnt % 200 == 0:
			print 'saving file...'
			with codecs.open('veer/fengguang.json', 'w', encoding='utf-8') as fout:
				json.dump(img_list, fout, ensure_ascii=False, encoding='utf-8', indent=4)
	if cnt % 200 != 0:
		print 'saving file...'
		with codecs.open('veer/fengguang.json', 'w', encoding='utf-8') as fout:
			json.dump(img_list, fout, ensure_ascii=False, encoding='utf-8', indent=4)
