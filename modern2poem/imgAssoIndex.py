# coding=utf-8
import os, re
import json
import codecs
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


# 与myresult文件夹和fengguang.json在同一目录下
class ImgAsso:
    def __init__(self, index_name='imgasso', index_type='imgasso_type'):
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self, index_name, index_type):
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "imgurl": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "imgsrc": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "desc": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "asso": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "analyzer": "whitespace",
                            "search_analyzer": "whitespace",
                        },
                        "usedtimes": {
                            "type": "integer",
                        }
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print (res)

    def bulk_Data(self):
        '''
        用bulk将批量的数据存储到es
        '''
        ACTIONS = []
        i = 1
        with codecs.open('fengguang.json', 'r', encoding='utf-8') as fin:
            imgfile = json.load(fin)
        for filename in os.listdir('myresult'):
            path = 'myresult/' + filename
            with codecs.open(path, 'r', encoding='utf-8') as fin:
                try:
                    asso = json.load(fin)
                except:
                    print(filename, 'cannot load json')
                    continue
            j = 0
            for j in range(len(imgfile)):
                if asso[0]['img'] == imgfile[j]['imgurl']:
                    break
            for item in asso:
                action = {
                    "_index": self.index_name,
                    "_type": self.index_type,
                    "_id": i,
                    "_source": {
                        "imgurl": item['img'],
                        "imgsrc": imgfile[j]['source'],
                        "desc": item['desc'],
                        "asso": ' '.join(item['asso']),
                        "usedtimes": 0
                    }
                }
                j += 1
                i += 1
                ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)


if __name__ == '__main__':
    imgasso = ImgAsso()
    print('indexing image associations...')
    imgasso.bulk_Data()
