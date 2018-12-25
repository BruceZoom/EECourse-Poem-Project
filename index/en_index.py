#!/usr/bin/env python
#-*- coding:utf-8 -*-
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time, re, jieba, json
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
import nltk.stem.porter as pt
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

def get_stem(doc):
    res=""
    stemmer = pt.PorterStemmer()
    token = nltk.word_tokenize(doc)
    for t in token:
        if t.isalpha():
            stem = stemmer.stem(t)
            res=res+stem+" "
    return res

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        self.root=root
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        self.store=store
        self.Analyzer=analyzer
        self.success=0

        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):
        # label
        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        # content
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        # likes imgurl text
        t3 = FieldType()
        t3.setIndexed(False)
        t3.setStored(True)
        t3.setTokenized(False)

        def addDoc(text,img,likes,content):
            try:
                doc = Document()
                doc.add(Field("imgurl", img, t3))
                doc.add(Field("likes", likes, t3))
                doc.add(Field("text", text, t3))
                doc.add(Field("content", content, t2))
                doc.add(Field("label", '', t1))
                writer.addDocument(doc)
                self.success += 1
            except Exception, e:
                print "Failed in indexDocs:", e
        # prepare info

        # en_with_img
        load_f = open(DATA_DIR + '/en_with_img.json', 'r')
        data = json.load(load_f)
        load_f.close()
        for poem in data:
            text = poem['poem']
            likes = ''
            img = poem['image_url']
            content = get_stem(text)
            # create index
            addDoc(text, img, likes, content)

        # en_without_img
        load_f = open(DATA_DIR + '/en_without_img.json', 'r')
        data = json.load(load_f)
        load_f.close()
        for poem in data:
            text = poem['poem']
            likes = ''
            img = ''
            content = get_stem(text)
            # create index
            addDoc(text, img, likes, content)



        print "%s documents indexed"%self.success

    def testDelete(self, fieldName, searchString):
        config = IndexWriterConfig(Version.LUCENE_CURRENT, self.Analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
        writer = IndexWriter(self.store, config)
        writer.deleteDocuments(Term(fieldName, searchString))
        writer.close()

def remove_repetition():
    load_f = open(DATA_DIR + '/cn_with_img.json', 'r')
    data = json.load(load_f)
    load_f.close()
    title=[]
    new_data=[]
    for poem in data:
        if poem['title'] not in title:
            title.append(poem['title'])
            new_data.append(poem)
        else:
            print poem['title']
    print "repetition: %s"% (len(data)-len(new_data))
    if len(data)-len(new_data)==0:
        return
    # useless
    '''
    with codecs.open('shiying_data.json','w') as f:
        json.dump(new_data,f,ensure_ascii=False,indent=4)
        print 'data file updated'
    '''


DATA_DIR=os.path.join('sourcePoems/modernPoems')
STORE_DIR="index/english"
if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    IndexFiles(DATA_DIR, STORE_DIR)
