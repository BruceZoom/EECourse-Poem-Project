#!/usr/bin/env python
#-*- coding:utf-8 -*-
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, jieba, json
import nltk
import nltk.stem.porter as pt
import translate as ts

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause



def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
def get_stem(doc):
    res=""
    stemmer = pt.PorterStemmer()
    token = nltk.word_tokenize(doc)
    for t in token:
        if t.isalpha():
            stem = stemmer.stem(t)
            res=res+stem+" "
    return res

class ModernPoemSearch:
    def __init__(self):
        self.chSearcher = IndexSearcher(DirectoryReader.open(SimpleFSDirectory(File('index/chinese'))))
        self.enSearcher = IndexSearcher(DirectoryReader.open(SimpleFSDirectory(File('index/english'))))
        self.Analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)



    def search(self,command,type):
        # type  all title author content
        num = 0 # total search results
        data1=[] # chinese results
        data2=[] # english results
        if command == '':
            return
        data=[]
        if not command.isalpha():
            chs=command
            eng=ts.zn_to_en_translate(command)
        else:
            chs=ts.en_to_zn_translate(chs)
            eng=command
        # segmentation
        try:
            seg_list = jieba.cut(chs)
            chs = ' '.join(seg_list)
        except:
            # print 'segmentation failed'
            pass
        eng = get_stem(eng)

        # chinese
        #booleanQuery
        querys = BooleanQuery()
        if type=='title':
            query = QueryParser(Version.LUCENE_CURRENT, 'title_tokened', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.MUST)
        elif type=='author':
            query = QueryParser(Version.LUCENE_CURRENT, 'author', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.MUST)
        elif type=='content':
            query = QueryParser(Version.LUCENE_CURRENT, 'content', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.MUST)
        else:
            query = QueryParser(Version.LUCENE_CURRENT, 'title_tokened', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.SHOULD)
            query = QueryParser(Version.LUCENE_CURRENT, 'content', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.SHOULD)
            query = QueryParser(Version.LUCENE_CURRENT, 'author', self.Analyzer).parse(chs)
            querys.add(query, BooleanClause.Occur.SHOULD)
        scoreDocs = self.chSearcher.search(querys, 200).scoreDocs
        # print "%s total matching documents." % len(scoreDocs)

        for i, scoreDoc in enumerate(scoreDocs):
            doc = self.chSearcher.doc(scoreDoc.doc)
            item={}
            item['title'] = doc.get('title')
            item['author'] = doc.get('author')
            item['text'] = doc.get('text')
            item['imgurl'] = doc.get('imgurl')
            item['likes'] = doc.get('likes')
            item['label'] = ''
            item['id']=doc.get('id')
            data1.append(item)
        num += len(scoreDocs)

        # english
        # booleanQuery
        querys = BooleanQuery()
        query = QueryParser(Version.LUCENE_CURRENT, 'content', self.Analyzer).parse(eng)
        querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = self.enSearcher.search(querys, 200).scoreDocs
        # print "%s total matching documents." % len(scoreDocs)

        for i, scoreDoc in enumerate(scoreDocs):
            doc = self.enSearcher.doc(scoreDoc.doc)
            item = {}
            item['title'] = doc.get('title')
            item['author'] = doc.get('author')
            item['text'] = doc.get('text')
            item['imgurl'] = doc.get('imgurl')
            item['likes'] = doc.get('likes')
            item['label'] = ''
            item['id'] = doc.get('id')
            data2.append(item)
        num += len(scoreDocs)
        return num, data1, data2


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    mps=ModernPoemSearch()
    print mps.search("flower光线",'title')
