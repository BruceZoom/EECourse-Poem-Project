import association

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import jieba
import jieba.analyse
import numpy as np
# import synonyms

es = Elasticsearch(['localhost:9200'])
associator = association.Associator()

results = helpers.scan(
        client=es,
        query={'query': {'match_all': {}}},
        scroll='5m',
        index='cnmodern',
        doc_type='cnmodern_type',
        timeout='1m'
    )

hits = []
t = 0
for res in results:
    t += 1
    if t >= 10:
        break
    # ws = jieba.cut(res['_source']['text'])
    # print(res['_source']['text'])
    ws = jieba.analyse.extract_tags(res['_source']['text'], topK=20, withWeight=True, allowPOS=('n', 'nr', 'ns'))
    # ws = jieba.analyse.extract_tags("蓝色的裤子和排节目才能穿的白球鞋", topK=20, withWeight=True, allowPOS=('n', 'nr', 'ns'))
    cnt = 0
    for w, _ in ws:
        if w in associator.assoDict.keys():
            print(w)
            cnt += 1
    hits.append(cnt)
np.savetxt('modern_label_test.txt', hits)
