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
                # note=soup.find('div',{'class':"noteCon"})
                viewed = soup.find('span', {'id': re.compile('^hitcount')}).get_text()
                # if not note:
                #    note='none'
                # else:
                #    note=note.get_text()

                item = {}
                item['poem'] = poem
                item['poet'] = poet
                item['date'] = date
                item['title'] = title
                # item['note']=note
                item['viewed'] = viewed
                # print "poem:",poem
                # print "poet:",poet
                # print "date:",date
                # print "title:",title
                # print "note:",note
                # print "viewed:",viewed.get_text()
                # print type(title)   unicode
                j = soup.find('div', {'class': "m-md b-t b-light text-left"})
                next_url_pos = j.findAll('a')[1]
                next_url = next_url_pos.get('href')
                next_url = urlparse.urljoin('http://www.zgshige.com/', next_url)
                # print "next_url:",next_url
                # global next_page

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
                # print page
                pass


NUM = 4
pages = ['http://www.zgshige.com/c/2018-12-08/7898144.shtml','http://www.zgshige.com/c/2018-12-06/7889857.shtml','http://www.zgshige.com/c/2018-12-06/7881165.shtml','http://www.zgshige.com/c/2018-12-07/7872589.shtml','http://www.zgshige.com/c/2018-12-05/7864418.shtml','http://www.zgshige.com/c/2018-12-04/7855168.shtml','http://www.zgshige.com/c/2018-12-03/7847124.shtml','http://www.zgshige.com/c/2018-12-02/7838128.shtml']
max_count = 50
count = 0
q = Queue.Queue()
resList = []
crawled=[]
threads = []
varLock = threading.Lock()

for i in pages:
    #print i
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
with codecs.open("result1.json", 'w') as f:
    json.dump(resList, f, ensure_ascii=False, indent=4)

