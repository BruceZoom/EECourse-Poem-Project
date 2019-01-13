# -*- coding: utf-8 -*-
import sys
import os
import urllib2
from bs4 import BeautifulSoup
import re
import urlparse
import codecs
import json

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
    if not os.path.isfile(path):
        return
    item={}
    item['text']=""
    isTitle=False
    f = open(path, 'r')
    content = f.read()
    soup = BeautifulSoup(content,features='html.parser')
    f.close()
    # get author and likes
    author=""
    likes=None
    i=soup.find('div',{'class','m-b-sm'})
    if not i:
        print 'Cannot find author and likes'
    try:
        likes=i.find('span',{'class','badge'}).text
    except:
        print 'Cannot find likes'
        likes=None
    try:
        au=i.text.split()[0]
        if au.find(u'：')!=-1:
            author=au.split(u'：')[1]
    except:
        print 'Cannot get author'
    item['author']=author.encode('utf8')
    item['likes']=likes.encode('utf8')
    i=soup.find('div', {'class', 'm-lg article'})
    if not i:
        print 'Cannot find content'
        return
    for p in i.findAll('p'):
        img=p.find('img')
        # if has image
        if img:
            # clear previous
            if len(item.keys())==5 and item['text']:
                item['text']=item['text'].encode('utf8')
                data.append(item.copy())
            item['img']=''
            item['title']=''
            item['text']=''
            # get image src
            src=img.get('src')
            item['img']=base_url+src
            isTitle=True
            # print src
        # if is author info
        if p.text and len(p.text)>60:
            break
        # if is title
        if p.text:
            if isTitle:
                item['title']=p.text.encode('utf8')
                isTitle=False
                continue
                # print p.text
            # if is text
            if not isTitle:
                item['text']+=(p.text+'\n')

data=[]

if __name__ == '__main__':
    #crawl_page()
    #crawl_content()
    for filename in os.listdir('rawpage'):
        print 'Extracting info from %s'%filename
        path='rawpage/'+filename
        fetch_info(path)

    with codecs.open('shiying_data.json','w') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
