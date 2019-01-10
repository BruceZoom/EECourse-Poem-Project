# coding:utf-8

import utils
import codecs, json
from elasticsearch import Elasticsearch
from PoemSearchES import process_query_results
import random, datetime

es = Elasticsearch(['localhost:9200'])
cnmodern_MAX = 5028
gushiwen_MAX = 22797
daily_random = random.Random()
daily_random.seed(datetime.datetime.now().strftime('%Y%m%d'))
labels = []


def __get_item(d, k):
    if k not in d.keys() or d[k] is None:
        return ''
    else:
        return d[k]


def get_random_poem(poemType='cnmodern', id_max=0, daily=False):
    if id_max < 0:
        # 精确搜索
        id = -id_max
    else:
        # 随机搜索
        if daily:
            id = daily_random.randint(1, id_max)
        else:
            id = random.randint(1, id_max)
    body = {
        "query": {
            "ids": {
                "type": poemType + '_type',
                "values": [id]
            }
        }
    }
    res = es.search(index=poemType, doc_type=poemType + '_type', body=body)
    if res['hits']['total']:
        tmppoem = res['hits']['hits'][0]['_source']
        # poem: formulated poem data
        poem = {
            'title': __get_item(tmppoem, 'title'),
            'content': __get_item(tmppoem, 'text'),
            'poet': __get_item(tmppoem, 'author'),
            'imgurl': __get_item(tmppoem, 'imgurl'),
            'poemurl': '/poempage?index=' + poemType + '&id=[' + str(id) + ']'
        }
        if poem['poet']:
            poem['poeturl'] = '/authorpage?author=[' + poem['poet'] + ']'
        else:
            poem['poeturl'] = '/notfound'
        label = __get_item(tmppoem, 'label_tokenized')
        if label:
            labels.extend(label.split())
        return poem
    else:
        return get_one_poem(poemType, id_max)


def get_landing_data():
    data = {}
    data['daily'] = get_random_poem('cnmodern', cnmodern_MAX, True)
    data['random_modern'] = []
    for i in range(3):
        data['random_modern'].append(get_random_poem('cnmodern', cnmodern_MAX, False))
    data['daily_ancient'] = get_random_poem('gushiwen', gushiwen_MAX, True)
    data['random_ancient'] = []
    for i in range(3):
        data['random_ancient'].append(get_random_poem('gushiwen', gushiwen_MAX, False))
    # get scenery
    randnum = daily_random.randint(1, cnmodern_MAX + gushiwen_MAX)
    if randnum <= cnmodern_MAX:
        data['scenery'] = get_random_poem('cnmodern', -randnum)
    else:
        data['scenery'] = get_random_poem('gushiwen', -(randnum - cnmodern_MAX))
    random.shuffle(labels)
    data['labels'] = [{'label': x, 'labelurl': '/index'} for x in labels[:5]]
    return data


if __name__ == '__main__':
    print get_landing_data()
