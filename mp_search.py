#!/usr/bin/env python
#-*- coding:utf-8 -*-
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, jieba, json

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

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""

def parseCommand(command):
    '''
    input: C title:T author:A language:L
    output: {'contents':C, 'title':T, 'author':A, 'language':L}

    Sample:
    input:'contenance title:henri language:french author:william shakespeare'
    output:{'author': ' william shakespeare',
                   'language': ' french',
                   'contents': ' contenance',
                   'title': ' henri'}
    '''
    allowed_opt = ['site']
    command_dict = {}
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            command_dict['contents'] = command_dict.get('contents', '') + ' ' + i
    return command_dict


def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        command = unicode(command, 'utf8')
        if command == '':
            return
        print
        print "Searching for:", command
        # segmentation
        content=command
        try:
            seg_list = jieba.cut(content)
            content = ' '.join(seg_list)
        except:
            print 'segmentation failed'

        #booleanQuery
        querys = BooleanQuery()
        query = QueryParser(Version.LUCENE_CURRENT, 'title', analyzer).parse(content)
        querys.add(query, BooleanClause.Occur.SHOULD)
        query = QueryParser(Version.LUCENE_CURRENT, 'content', analyzer).parse(content)
        querys.add(query, BooleanClause.Occur.SHOULD)
        scoreDocs = searcher.search(querys, 200).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            print "------------------------"
            print 'title:', doc.get('title')
            print 'author:', doc.get('author')
            print 'text:', doc.get('text')
            print 'score:', scoreDoc.score
            # print 'explain:', searcher.explain(query, scoreDoc.doc)
        print "%s total matching documents." % len(scoreDocs)


if __name__ == '__main__':
    STORE_DIR = "index/modern"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher
