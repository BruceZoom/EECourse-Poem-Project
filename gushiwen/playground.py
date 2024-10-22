#coding=utf-8

from bs4 import BeautifulSoup
import urllib2
import urlparse
import json
import codecs


base_url = "https://www.gushiwen.org/shiwen/"

def get_shiwen_page(url):
	req = urllib2.Request(url, None, {'User-Agent': 'Custom User Agent'})
	response = urllib2.urlopen(req)
	soup = BeautifulSoup(response.read())
	res = []
	next_url = None

	try:
		left = soup.findAll('div', {'class': r'left'})
		try:
			sons = left[1].findAll('div', {'class': r'sons'})
		except:
			print 'no division named "left" is found'
			sons = soup.findAll('div', {'class': r'sons'})
		for son in sons:
			cont = son.find('div', {'class': r'cont'})
			title = cont.p.a.b.string
			info = [e.string for e in cont.find('p', {'class': r'source'}).findAll('a')]
			contsons = cont.find('div', {'class': r'contson'})
			try:
				song = ''.join([sent.string.strip() for sent in contsons.contents[::2]])
			except:
				print 'song format changed to <p>'
				song = ''.join([p.string for p in contsons.findAll('p')])
			rating = int(son.find('div', {'class': r'good'}).a.span.string.strip())
			try:
				tags = [tag.string for tag in son.find('div', {'class': r'tag'}).findAll('a')]
			except:
				print 'no division named "tag" is found'
				tags = []
			res.append({
				'title': title,
				'info': info,
				'song': song,
				'rating': rating,
				'tags': tags
			})
	except Exception, e:
		print e.message

	next_url = soup.find('a', {'class': r'amore'}).get('href')
	if next_url:
		next_url = urlparse.urljoin(base_url, next_url)
	return res, next_url


if __name__ == '__main__':
	res_all = []
	res_page, next_url = get_shiwen_page("https://m.gushiwen.org/shiwen/default.aspx?page=1000&type=0&id=0")
	print next_url
	# res_all += res_page
	# res_page, _ = get_shiwen_page(next_url)
	# res_all += res_page
	# # res_js = json.dumps(res_all)
	# with codecs.open('data/res_test.json', 'w', encoding='utf-8') as f:
	# 	json.dump(res_all, f, indent=4)
