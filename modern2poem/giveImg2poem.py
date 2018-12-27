# /usr/bin/env python
# -*- coding: utf-8 -*-
# 实现给每一首诗配图
import json,codecs
import os, re
import json
import codecs
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

def _getkey(dict, key):
    try:
        return dict[key]
    except:
        return None

_resdir='此处为有全部imgasso***.json数据的myresult文件夹'

'''这是用诗搜描述，不知效果如何；有对图片建索引的操作；我倾向于用描述搜诗
class ImagesObj:#给图片构造一个索引，方便后面的配图
    def __init__(self,index_name='image',index_type='image_type',resdir=_resdir):
        self.dir=resdir
        self.index_name =index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self,index_name,index_type):
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "desc":{
                            "type":"text",
                            "index":True,
                            "analyzer":"ik_max"
                        },
                        "asso": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "analyzer": "whitespace"
                        },
                        "Imageurl":{
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "usedtimes":{
                            "type":"integer",
                        }
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print (res)

    def bulk_Images_Data(self,list):
        ACTIONS = []
        i = 1
        for line in list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "desc":_getkey(line,'desc'),
                    "asso": _getkey(line,'asso'),
                    "Imageurl": _getkey(line,'img'),
                    "usedtimes":0
                }
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)

    def make_index_from_dir(self):
        wholeImageSet = []
        for root, _, files in os.walk(self.dir):
            for filename in files:
                with open(os.path.join(root, filename)) as fin:
                    oneList = json.load(fin)
                wholeImageSet.extend([{
                    'desc': x['desc'],
                    'img': x['img'],
                    'asso': ' '.join(x['asso'])
                } for x in oneList])
        print('indexing images...')
        self.bulk_Images_Data(wholeImageSet)

    def giveimg2gushiwen(self):
        #对所有古诗文（目前都没有配图）自动补全配图
        for poem in ['gushiwen索引中所有的古诗文']:break
            
            #用poem的text去搜索img的asso，不知道效果怎么样，可以试试
            #搜出来的img结果的前十个（按照相关度），再按照其usedtimes选项逆序排，取第一个，以尽可能让图片分散
            #对取的图片，usedtimes+=1
            
        #用类似的方法对现代诗索引，现代诗搜索时增大desc的比重，而对于英文诗，直接在veer文件夹内对其alt搜索

if __name__=="__main__":
    obj = ImagesObj()
    obj.make_index_from_dir()

'''
if __name__=="__main__":
    wholeImageSet = []
    for root, _, files in os.walk(_resdir):
        for filename in files:
            with open(os.path.join(root, filename)) as fin:
                oneList = json.load(fin)
            wholeImageSet.extend(oneList)
    wholeImageSet=[(x,0)for x in wholeImageSet]

    while(len('目前Imageurl为空的古诗')):
        #使用ES索引语句
        img,usedtime=wholeImageSet[0][0],wholeImageSet[0][1]
        try:desc=img['desc'][5*usedtime:5*usedtime+5]#按照相关顺序，每次取5个；也可以直接随机从asso中找词
        except:desc=img['desc']
        desc=''.join(desc)
        respoem='对所有Imageurl为空的gushiwen，使用desc为query得到的第一个结果；query以whitespace为分词（利用热词和ik，不用特别设置）'

        #更新respoem的Imageurl字段

        wholeImageSet[0][1]+=1
        wholeImageSet.sort(key=lambda x:x[1])#没被使用过的图片优先

    #对cnmodern、enmodern使用类似的方法配对图片。cnmodern可用desc和asso配合搜；英文直接到veer文件夹内的原始文件匹配


    #这种方法考虑到最后或许会有一些poem始终没有图也不被搜到。随机赋值？在asso中随机找词搜索？


