import sys
import os
import urllib2
from bs4 import BeautifulSoup
import re
import urlparse
import codecs

base_url='http://www.zgshige.com'
def crawl_page():
    pageNum = 2
    for pageNum in range(1,11):
        url='http://www.zgshige.com/syzg'
        if pageNum>1:
            url += '/index_' + str(pageNum) + '.shtml'
        content=None
        try:
            content = urllib2.urlopen(url).read()
        except:
            print 'Connection failed.'
        if content:
            print 'Page'+str(pageNum)+' crawled'
        else:
            continue
        f = open('shiying/shiyingpage'+str(pageNum)+'.html', 'w')
        f.write(content)
        f.close()

def crawl_content():
    p=re.compile('<a class="h4 bold" href="(.*)" target')
    counts=0
    for filename in os.listdir('shiying'):
        f=open('shiying/'+filename,'r')
        content=f.read()
        for postfix in re.findall(p,content):
            url=base_url+postfix
            header = {
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            req = urllib2.Request(url, headers=header)
            content = None
            try:
                content = urllib2.urlopen(req).read()
            except:
                print 'Connection failed.'
            if content:
                counts+=1
                print 'Content' + str(counts) + ' crawled'
            else:
                continue
            f = open('shiying/shiying' + str(counts) + '.html', 'w')
            f.write(content)
            f.close()
def fetch_info(path):
    print path
    if not os.path.isfile(path):
        return
    print path
    f = open(path, 'r')
    content = f.read()
    soup = BeautifulSoup(content)
    f.close()
    for i in soup.findAll('div', {'class', 'm-lg article'}):
        p=re.compile('<p>.*</p')
        print re.findall(p,str(i))



if __name__ == '__main__':
    #crawl_page()
    #crawl_content()
    for filename in os.listdir('shiying'):
        path='shiying/'+filename
        fetch_info(path)
        break