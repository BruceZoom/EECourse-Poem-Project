#!/usr/bin/env python
#coding=utf-8

INDEX_DIR = "IndexPoems.index"
import nltk
import json
import jieba
import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
# from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setIndexed(False)
        t1.setStored(True)
        t1.setTokenized(False)

        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        path="./shi/poet.song.%s.json" %(str(root))
        print path
        with open(path, 'r') as load_f:
            load_dict = json.load(load_f)
        count=0
        for dic in load_dict:
            try:
                print "new item!"
                values = dic.values()
                # print len(values)
                strains = values[0][0].encode('utf-8')
                print "strains:", strains
                paragraphs = values[1][0].encode('utf-8')
                print "paragraphs:", paragraphs
                title = values[2].encode('utf-8')
                print "title:", title
                author = values[3].encode('utf-8')
                print "author:", author
                doc = Document()
                doc.add(Field("strains", strains, t1))
                doc.add(Field("paragraphs_untokened", paragraphs, t1))
                doc.add(Field("title_untokened", title, t1))
                doc.add(Field("author", author, t1))

                seg_list1 = jieba.cut(paragraphs)
                paragraphs_tokened = " ".join(seg_list1)
                seg_list2=jieba.cut(title)
                title_tokened = " ".join(seg_list2)
                doc.add(Field("paragraphs_tokened", paragraphs_tokened, t2))
                doc.add(Field("title_tokened", title, t2))
                writer.addDocument(doc)
                count += 1
                print count
            except:
                pass


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        for i in range(0,1):
            IndexFiles('%s'%(i), "song_index%s"%(i))
        end = datetime.now()
        print end - start
    except Exception, e:
        print("Failed: {}".format(e))
        raise e