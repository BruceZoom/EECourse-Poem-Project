#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import os
import lucene
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from java.io import File
from org.apache.lucene.analysis.core import SimpleAnalyzer
#from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause


def parseCommand(command):
    allowed_opt = ['author','dynasty']
    command_list=[]
    for i in command.split(' '):
        i=i.encode('utf-8')
        if ':' in i:
            opt,value = i.split(':')[:2]
            if opt in allowed_opt:
                command_list.append(i)
    return command_list


class AncientPoemSearcher(object):
    def __init__(self, folder='gushiwen_index'):
        self.searcher = IndexSearcher(DirectoryReader.open(SimpleFSDirectory(File(folder))))
        self.analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)

    def gushiwen_search(self,  command_dict, target_range=None,
                        targets=('paragraghs_untokened', 'title_untokened', 'dynasty', 'author', 'label', 'yiwen'
                                 'shangxi', 'imgurl')):
        res = []

        querys = BooleanQuery()
        for key, value in command_dict.items():
            query = QueryParser(Version.LUCENE_CURRENT, key, self.Analyzer).parse(value[0])
            if value[1]:
                querys.add(query, BooleanClause.Occur.MUST)
            else:
                querys.add(query, BooleanClause.Occur.SHOULD)
        totalDocs = self.chSearcher.search(querys, utils.MAX_RESULTS).scoreDocs

        total_match = len(totalDocs)
        if target_range is None:
            scoreDocs = totalDocs[:]
        else:
            scoreDocs = totalDocs[max(0, target_range[0]), min(total_match, target_range[1])]
        del totalDocs

        for i, scoreDoc in enumerate(scoreDocs):
            doc = self.chSearcher.doc(scoreDoc.doc)
            res.append({key: doc.get(key) for key in targets})

        return total_match, res


def searchPoems(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        command = unicode(command, 'utf8')
        if command == '':
            return

        print
        print "Searching for:", command
        querys = BooleanQuery()
        content_search=command.split(' ')[0]
        seg_list = jieba.cut(content_search)
        my_content = " ".join(seg_list)
        print "content_search is:",content_search
        query_content = QueryParser(Version.LUCENE_CURRENT, "paragraphs_tokened",
                            analyzer).parse(my_content)
        querys.add(query_content, BooleanClause.Occur.MUST)
        query_title = QueryParser(Version.LUCENE_CURRENT, "title_tokened",
                            analyzer).parse(my_content)
        querys.add(query_title, BooleanClause.Occur.SHOULD)

        option_list = parseCommand(command)
        for i in option_list:
            option_name=unicode(i.split(':')[0])
            option_value=i.split(':')[1].decode('utf-8')
            print option_name,"search:",option_value
            query = QueryParser(Version.LUCENE_CURRENT, option_name,
                                analyzer).parse(option_value)
            querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = searcher.search(querys, 10000000).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            #explanation = searcher.explain(query, scoreDoc.doc)
            print 'title:', doc.get('title_untokened')
            print 'dynasty', doc.get('dynasty'),' author:', doc.get('author')
            print type(doc.get('author'))
            print 'paragraphs:\n', doc.get('paragraphs_untokened')
            print 'score:', scoreDoc.score
            #print explanation


if __name__ == '__main__':
    STORE_DIR = "./gushiwen_index"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
    searchPoems(searcher, analyzer)
    del searcher