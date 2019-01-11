# coding:utf-8

# import codecs, json
from elasticsearch import Elasticsearch
from PoemSearchES import process_query_results
import random
import datetime

es = Elasticsearch(['localhost:9200'])
cnmodern_MAX = 5028
gushiwen_MAX = 22797
daily_random = random.Random()
today = datetime.datetime.now().strftime('%Y%m%d')
daily_random.seed(today)
daily_cnmodern_id = daily_random.randint(1, cnmodern_MAX)
daily_gushiwen_id = daily_random.randint(1, gushiwen_MAX)
daily_scenery_id = daily_random.randint(1, cnmodern_MAX + gushiwen_MAX)
labels = []


def __get_item(d, k):
    if k not in d.keys() or d[k] is None:
        return ''
    else:
        return d[k]


def get_random_poem(poemType='cnmodern', id_max=1, daily=False):
    if daily:
        id = id_max
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
        if len(poem['content']) > 50 * 3:
            return get_random_poem(poemType, id + 1, True)
        if poem['poet']:
            poem['poeturl'] = '/authorpage?author=[' + poem['poet'] + ']'
        else:
            poem['poeturl'] = '/notfound'
        label = __get_item(tmppoem, 'label_tokenized')
        if label:
            labels.extend(label.split())
        return process_query_results(poem)
    else:
        return get_random_poem(poemType, id_max)


def get_landing_data():
    data = {}
    # check the date
    if today != datetime.datetime.now().strftime('%Y%m%d'):
        globals()['today'] = datetime.datetime.now().strftime('%Y%m%d')
        daily_random.seed(today)
        globals()['daily_cnmodern_id'] = daily_random.randint(1, cnmodern_MAX)
        globals()['daily_gushiwen_id'] = daily_random.randint(1, gushiwen_MAX)
        globals()['daily_scenery_id'] = daily_random.randint(1, cnmodern_MAX + gushiwen_MAX)
    data['daily'] = get_random_poem('cnmodern', daily_cnmodern_id, True)
    data['random_modern'] = []
    for i in range(3):
        data['random_modern'].append(get_random_poem('cnmodern', cnmodern_MAX, False))
    data['daily_ancient'] = get_random_poem('gushiwen', daily_gushiwen_id, True)
    data['random_ancient'] = []
    for i in range(3):
        data['random_ancient'].append(get_random_poem('gushiwen', gushiwen_MAX, False))
    # get scenery
    if daily_scenery_id <= cnmodern_MAX:
        data['scenery'] = get_random_poem('cnmodern', daily_scenery_id, True)
    else:
        data['scenery'] = get_random_poem('gushiwen', daily_scenery_id - cnmodern_MAX, True)
    random.shuffle(labels)
    data['labels'] = [{'label': x, 'labelurl': '/index'} for x in labels[:5]]
    return data

# LANDING_DATA = get_landing_data()

# if __name__ == '__main__':
# print get_landing_data()['daily']
# print get_landing_data()['daily']
