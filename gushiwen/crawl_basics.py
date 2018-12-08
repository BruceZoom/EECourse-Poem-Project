#coding=utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib2
import urlparse
import json
import codecs
import sys


def get_shiwen_page(base, url, driver=None, skip=False):
	req = urllib2.Request(url, None, {'User-Agent': 'Custom User Agent'})
	response = urllib2.urlopen(req)
	soup = BeautifulSoup(response.read())
	res = []
	next_url = None

	if not skip:
		try:
			left = soup.findAll('div', {'class': r'left'})
			try:
				sons = left[1].findAll('div', {'class': r'sons'})
			except:
				# print 'no division named "left" is found'
				sons = soup.findAll('div', {'class': r'sons'})
			for son in sons:
				#  retrieve basic info
				cont = son.find('div', {'class': r'cont'})
				title = cont.p.a.b.string
				info = [e.string for e in cont.find('p', {'class': r'source'}).findAll('a')]

				#  prepare for js retrieval
				contsons = cont.find('div', {'class': r'contson'})
				id_suffix = contsons['id'][7:]
				if driver:
					driver.get(url)
					id_prefixes = ['zhushi', 'yiwen']
					contson_elem = driver.find_element_by_css_selector('#contson' + id_suffix)
				extra = {}

				#  retrieve song content
				try:
					# song = [sent.strip() for sent in contsons.contents[::2]]
					song = []
					for sent in contsons.contents:
						try:
							if sent.strip() != '':
								song.append(sent.strip())
						except:
							for sent1 in sent.contents:
								try:
									if sent1.strip() != '':
										song.append(sent1.strip())
								except:
									pass
							pass
					assert ''.join(song) != ''
				except:
					# print 'song format changed to <p>'
					song = []
					for p in contsons.findAll('p'):
						try:
							if p.string.strip() != '':
								song.append(p.string.strip())
						except:
							pass

				#  retrieve js
				if driver:
					for prefix in id_prefixes:
						btn_id = '#btn' + prefix.title() + id_suffix
						driver.find_element_by_css_selector(btn_id).click()
						extra[prefix] = []
						ps = contson_elem.find_elements_by_tag_name('p')
						for p in ps:
							try:
								extra[prefix].append(p.find_element_by_tag_name('span').text)
							except:
								pass
						driver.find_element_by_css_selector(btn_id).click()

				#  retrieve shangxi
				if driver:
					try:
						btn_id = '#btnShangxi' + id_suffix
						driver.find_element_by_css_selector(btn_id).click()
						ps = contson_elem.find_elements_by_tag_name('p')[len(song):]
						extra['shangxi'] = [p.text for p in ps]
						driver.find_element_by_css_selector(btn_id).click()
					except Exception, e:
						print e.message
						extra['shangxi'] = []

				#  retrieve other things
				rating = int(son.find('div', {'class': r'good'}).a.span.string.strip())
				try:
					tags = [tag.string for tag in son.find('div', {'class': r'tag'}).findAll('a')]
				except:
					# print 'no division named "tag" is found'
					tags = []

				res.append({
					'title': title,
					'info': info,
					'song': song,
					'rating': rating,
					'tags': tags,
					'extra': extra
				})
		except Exception, e:
			print e.message

	next_url = soup.find('a', {'class': r'amore'}).get('href')
	if next_url:
		next_url = urlparse.urljoin(base, next_url)
	return res, next_url


def crawl_loop(get_one_page, seed, max_loop=-1):
	res_all = []
	next_url = seed
	cnt = 0
	while next_url and (max_loop <= -1 or max_loop > 0):
		if cnt % 10 == 0:
			print 'current page', cnt+1
		try:
			res_page, next_url = get_one_page(seed, next_url)
		except:
			break
		res_all += res_page
		max_loop -= 1
		cnt += 1
	return res_all


def crawl_loop_js(get_one_page, seed, max_loop=-1, skip_to=None, batch=10):
	res_all = []
	next_url = seed
	cnt = 0
	driver = webdriver.Firefox()
	while next_url and (max_loop <= -1 or max_loop > 0):
		if skip_to is None:
			if cnt > 0 and cnt % batch == 0:
				with codecs.open('data/res_test_{}.json'.format(cnt//batch), 'w', encoding='utf-8') as f:
					json.dump(res_all, f, indent=4, encoding='utf-8', ensure_ascii=False)
				res_all = []
			try:
				res_page, next_url = get_one_page(seed, next_url, driver)
			except Exception, e:
				print e
				break
			res_all += res_page
			max_loop -= 1
		else:
			print cnt, skip_to * batch
			_, next_url = get_one_page(seed, next_url, driver, skip=True)
			if cnt >= skip_to * batch:
				skip_to = None
			# if cnt > 0 and cnt % batch == 0:
			# 	skip_to -= 1
			# 	if skip_to < 1:
			# 		skip_to = None
		cnt += 1
		print 'current progress: ', cnt
	driver.quit()
	with codecs.open('data/res_test_tail.json', 'w', encoding='utf-8') as f:
		json.dump(res_all, f, indent=4, encoding='utf-8', ensure_ascii=False)
	return res_all

if __name__ == '__main__':
	max_loop = -1
	skip_to = None
	if len(sys.argv) >= 2:
		max_loop = int(sys.argv[1])
	if len(sys.argv) >= 3:
		skip_to = int(sys.argv[2])
	res_all = crawl_loop_js(get_shiwen_page, "https://www.gushiwen.org/shiwen/", max_loop=max_loop, skip_to=skip_to)
	# res_all = crawl_loop(get_shiwen_page, "https://www.gushiwen.org/shiwen/", max_loop=3)
	# with codecs.open('data/res_test.json', 'w', encoding='utf-8') as f:
	# 	json.dump(res_all, f, indent=4, encoding='utf-8', ensure_ascii=False)
