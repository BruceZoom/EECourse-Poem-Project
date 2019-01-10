import json
from elasticsearch import Elasticsearch
import codecs
import jieba.analyse

es = Elasticsearch()

# update the author,add three columns
# print('updating author...')
# with codecs.open('allauthors.json', 'r', encoding='utf-8')as fin:
#     authorList = json.load(fin)
# index_name = 'author'
# index_type = 'author_type'
# len=len(authorList)
# print("len of authors is:",len)
# for i in range(1,len):
#     print("updating nunber:",i)
#     es.update(index=index_name,doc_type=index_type,id=i,body={"doc":{"time_text":"","time_key":"","genre":""}})

# update cnmodern label_tokenized
print('updating cnmodern...')
with codecs.open('../../allchinesemoderns.json', 'r', encoding='utf-8')as fin:
    cnmodernList = json.load(fin)
index_name = 'cnmodern'
index_type = 'cnmodern_type'
le = len(cnmodernList)
print("len of poems is:", le)
for i in range(1, le):
    print("{}/{}".format(i, le))
    result = es.get(index=index_name, doc_type=index_type, id=i)
    text = result['_source']['text']
    # print(text)
    label_tokenized = '\n'.join(jieba.analyse.extract_tags(text, topK=5, withWeight=False, allowPOS=('n', 'ns')))
    print(label_tokenized)
    updateBody = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"_id": i}}
                ],
            }
        },
        "script": {
            "inline": "ctx._source.label_tokenized = params.label;ctx._source.label = params.label",
            "params": {
                "label": label_tokenized,
                "label_tokenized": label_tokenized
            },
            "lang": "painless"
        }
    }
    es.update_by_query(index=index_name, doc_type=index_type, body=updateBody)

# update gushiwen label_tokenized
# jieba.set_dictionary('guci_dict.txt')
# guci_analyzer = jieba.analyse.TFIDF(idf_path='guci_idf.txt')
# print('updating gushiwen...')
# with codecs.open('../../allpoems.json', 'r', encoding='utf-8')as fin:
#     gushiwenList = json.load(fin)
# index_name = 'gushiwen'
# index_type = 'gushiwen_type'
# le = len(gushiwenList)
# print("len of poems is:", le)
# for i in range(1, le):
#     print("{}/{}".format(i, le))
#     result = es.get(index=index_name, doc_type=index_type, id=i)
#     text = result['_source']['text']
#     label = result['_source']['label']
#     print(text)
#     label_tokenized = '\n'.join(guci_analyzer.extract_tags(text, topK=3, withWeight=False))
#     label = label + '\n' + label_tokenized
#     print(label)
#     updateBody = {
#         "query": {
#             "bool": {
#                 "must": [
#                     {"term": {"_id": i}}
#                 ],
#             }
#         },
#         "script": {
#             "inline": "ctx._source.label = params.label;ctx._source.label_tokenized=params.label",
#             "params": {
#                 "label": label,
#                 "label_tokenized": label
#             },
#             "lang": "painless"
#
#         }
#     }
#     es.update_by_query(index=index_name, doc_type=index_type, body=updateBody)
