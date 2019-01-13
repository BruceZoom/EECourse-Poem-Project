# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2
import threading
import Queue
import re
import urlparse
from bs4 import BeautifulSoup
import json
import codecs


def crawl():
    global count
    global max_count
    while (True):
        page = q.get()
        if page not in crawled:
            try:
                response = urllib2.urlopen(page, timeout=3)
                content = response.read()
                soup = BeautifulSoup(content, features="html.parser")
                title = soup.find('div', {'class': "text-center b-b b-2x b-lt"}).get_text(strip=True).rstrip('\n').lstrip(
                    '\n').replace(' ', '')
                poem = soup.find('div', {'class': "m-lg font14"}).get_text()
                poet = soup.find('div', {'class': "col-xs-12"}).contents[1].get_text(strip=True)
                poet = poet.replace('\t', '').replace('作者：\n', '')
                date = soup.find('div', {'class': "col-xs-12"}).contents[2].get_text(strip=True)
                viewed = soup.find('span', {'id': re.compile('^hitcount')}).get_text()

                item = {}
                item['poem'] = poem
                item['poet'] = poet
                item['date'] = date
                item['title'] = title
                item['viewed'] = viewed
                j = soup.find('div', {'class': "m-md b-t b-light text-left"})
                next_url_pos = j.findAll('a')[1]
                next_url = next_url_pos.get('href')
                next_url = urlparse.urljoin('http://www.zgshige.com/', next_url)
                if varLock.acquire():
                    count+=1
                    print count
                    if count > max_count:
                        varLock.release()
                        q.task_done()
                        break
                    item['id']=count
                    q.put(next_url)
                    crawled.append(page)
                    resList.append(item)
                    varLock.release()
                q.task_done()
            except:
                pass

def get_seed(resNum):
    pageNum = (resNum - 1) * 25
    seeds=[]
    for i in range(pageNum,pageNum+24,3):
        print 'Getting seed from page %s'%i
        url = 'http://www.zgshige.com/zcms/catalog/15130/pc/index_' + str(i) + '.shtml'
        try:
            content = urllib2.urlopen(url).read()
        except:
            print 'Connection failed'
            continue
        soup=BeautifulSoup(content,features="html.parser")
        a=soup.find('a',{'class':'fc-green text-uppercase'})
        if not a:
            print 'Cannot get info'
            continue
        seed=a.get('href','')
        if seed:
            seeds.append(seed)
    print seeds
    return seeds,150*len(seeds)



NUM = 4
resNum = 401

pages,max_count=get_seed(resNum) # 401 for seeds start from page 10000, 25 page per turn
print 'max_count:%s'%max_count
count = 0
q = Queue.Queue()
resList = []
crawled=[]
threads = []
varLock = threading.Lock()

for i in pages:
    q.put(i)

for i in range(NUM):
    t = threading.Thread(target=crawl)
    t.setDaemon(True)
    threads.append(t)

# start each thread
for t in threads:
    t.start()

# join threads
for t in threads:
    t.join()

print "length of crawled:",len(crawled)
with codecs.open("result"+str(resNum)+".json", 'w') as f:
    json.dump(resList, f, ensure_ascii=False, indent=4)

