# coding=utf-8
import json
from elasticsearch import Elasticsearch
import codecs
from elasticsearch.helpers import bulk

es=Elasticsearch()
#以下均为试验
#es.index(index="my_index",doc_type="test_type",id=1,body={"name":"张三","addr":"深圳"})
#es.index(index="my_index",doc_type="test_type",id=2,body={"name":"李四","addr":"广州"})
# index_name = 'my_index'
# index_type = 'test_type'

# searchBody = {
#     "query":{
#          "term":{
#                 "_id":1
#          }
#      },
# }
# se=es.search(index=index_name,doc_type=index_type,body=searchBody)
# print(se)
# print(se['hits']['hits'][0]['_source']['name'])
# print(type(se['hits']['hits'][0]['_source']['name']))
# print(se.keys())


# updateBody = {
#     "query":{
#          "bool":{
#              "must":[{
#                  "term":{
#                      "name":"张"
#                  }
#              },
#             {
#                  "term":{
#                      "name":"三"
#                  }
#              }
#              ]
#          }
#      },
#     "script": {
#         "source": "ctx._source.time_text = params.time_text;ctx._source.time_key = params.time_key;ctx._source.genre = params.genre",
#
#         "params": {
#                 "time_text":"123213",
#                 "time_key":"2342",
#                 "genre":""
#         },
#         "lang":"painless"
#     }
# }
# es.update_by_query(index=index_name,doc_type=index_type,body=updateBody)

#删除所有索引
# body = {
#     "query":{
#         "match_all":{}
#     }
# }
# es.delete_by_query(index=index_name,doc_type=index_type,body=body)

#添加空项
# index_name = 'cnmodern'
# index_type = 'cnmodern_type'
# updateBody = {
#    "query":{
#          "match_all":{}
#      },
#     "script": {
#         "source": "ctx._source.time_text = params.time_text;ctx._source.time_key = params.time_key;ctx._source.genre = params.genre",
#
#         "params": {
#                 "time_text":"",
#                 "time_key":"",
#                 "genre":""
#         },
#         "lang":"painless"
#     }
# }
#
# es.update_by_query(index=index_name,doc_type=index_type,body=updateBody)

with codecs.open('../cnmodern_author_info.json', 'r', encoding='utf-8') as fin:
    oneList = json.load(fin)
index_name = 'cnmodern'
index_type = 'cnmodern_type'
for item in oneList:
    author=item['author']
    time_key=item['time_key']
    time_text=item['time_text']
    genre=item['genre']
    #str
    print(author)
    print(len(author))
    print(time_text)
    #把人名拆成一个字一个字，全部匹配，结果没匹配上
    # must=[]
    # for i in range(0,len(author)):
    #     item={}
    #     term={}
    #     term["name"]=author[i]
    #     item["term"]=term
    #     must.append(item)
    # print(must)
    # updateBody = {
    #    "query":{
    #          "bool":{
    #              "must":must
    #          }
    #      },
    #     "script": {
    #         "source": "ctx._source.time_text = params.time_text;ctx._source.time_key = params.time_key;ctx._source.genre = params.genre",
    #
    #         "params": {
    #                 "time_text":time_text,
    #                 "time_key":time_key,
    #                 "genre":genre
    #         },
    #         "lang":"painless"
    #     }
    # }
    #

    #用match_phrase方法匹配，没匹配上
    updateBody = {
       "query":{
             "match_phrase":{
                 "author":author
             }
         },
        "script": {
            "source": "ctx._source.time_text = params.time_text;ctx._source.time_key = params.time_key;ctx._source.genre = params.genre",

            "params": {
                    "time_text":time_text,
                    "time_key":time_key,
                    "genre":genre
            },
            "lang":"painless"
        }
    }

    es.update_by_query(index=index_name,doc_type=index_type,body=updateBody)
