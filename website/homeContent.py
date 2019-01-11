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
# labels = []


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
        if not daily:
            return process_query_results(res['hits']['hits'])[0], res['hits']['hits'][0]['_source']['label']
        # labels = []
        # searchType = {'cnmodern': 'modern', 'gushiwen': 'ancient'}[poemType]
        # for tmp in res['hits']['hits']:
        #     print(tmp)
        #     labels += [{
        #         'label': label,
        #         'labelurl': '/gallery?searchType=' + searchType + '&image=&label=on&query=' + label,
        #     }
        #     for label in tmp['_source']['label'].split()]
        # label = __get_item(tmppoem, 'label_tokenized')
        # if label:
        #     labels.extend(label.split())
        # if len(res['hits']['hits'][0]['_source']['text']) > 200:
        #     return get_random_poem(poemType, id + 1, True)
        # print(labels)
        # print()
        # print()
        # print()
        # print()
        # print()
        # print()
        # print(res['hits']['hits'][0]['_source']['label'])
        return process_query_results(res['hits']['hits'])[0], res['hits']['hits'][0]['_source']['label']
        # return process_query_results(res['hits']['hits'])[0], labels

        # tmppoem = res['hits']['hits'][0]['_source']['text']
        # poem: formulated poem data
        # poem = {
        #     'title': __get_item(tmppoem, 'title'),
        #     'content': __get_item(tmppoem, 'text'),
        #     'poet': __get_item(tmppoem, 'author'),
        #     'imgurl': __get_item(tmppoem, 'imgurl'),
        #     'poemurl': '/poempage?index=' + poemType + '&id=' + str(id)
        # }
        # if len(poem['content']) > 50 * 3:
        #     return get_random_poem(poemType, id + 1, True)
        # if poem['poet']:
        #     poem['poeturl'] = '/authorpage?author=' + poem['poet']
        # else:
        #     poem['poeturl'] = '/notfound'
    else:
        # print('fdasfndsaihfndsaifanifdn')
        return get_random_poem(poemType, id_max)


def get_landing_data():
    data = {}
    # check the date
    global today
    if today != datetime.datetime.now().strftime('%Y%m%d'):
        today = datetime.datetime.now().strftime('%Y%m%d')
        daily_random.seed(today)
        globals()['daily_cnmodern_id'] = daily_random.randint(1, cnmodern_MAX)
        globals()['daily_gushiwen_id'] = daily_random.randint(1, gushiwen_MAX)
        globals()['daily_scenery_id'] = daily_random.randint(1, cnmodern_MAX + gushiwen_MAX)
    labels = []
    data['daily'], label = get_random_poem('cnmodern', daily_cnmodern_id, True)
    labels += [{
        'label': tmp,
        'labelurl': '/gallery?searchType=' + 'modern' + '&image=&label=on&query=' + tmp,
    } for tmp in label.split()]
    data['random_modern'] = []
    for i in range(3):
        song, label = get_random_poem('cnmodern', cnmodern_MAX, False)
        # print(tmp)
        data['random_modern'].append(song)
        labels += [{
            'label': tmp,
            'labelurl': '/gallery?searchType=' + 'modern' + '&image=&label=on&query=' + tmp,
        } for tmp in label.split()]
    data['daily_ancient'], label = get_random_poem('gushiwen', daily_gushiwen_id, True)
    labels += [{
        'label': tmp,
        'labelurl': '/gallery?searchType=' + 'ancient' + '&image=&label=on&query=' + tmp,
    } for tmp in label.split()]
    # labels += tmp
    data['random_ancient'] = []
    for i in range(3):
        song, label = get_random_poem('gushiwen', gushiwen_MAX, False)
        data['random_ancient'].append(song)
        labels += [{
            'label': tmp,
            'labelurl': '/gallery?searchType=' + 'ancient' + '&image=&label=on&query=' + tmp,
        } for tmp in label.split()]
    # get scenery
    if daily_scenery_id <= cnmodern_MAX:
        data['scenery'], label = get_random_poem('cnmodern', daily_scenery_id, True)
        labels += [{
            'label': tmp,
            'labelurl': '/gallery?searchType=' + 'modern' + '&image=&label=on&query=' + tmp,
        } for tmp in label.split()]
    else:
        data['scenery'], label = get_random_poem('gushiwen', daily_scenery_id - cnmodern_MAX, True)
        labels += [{
            'label': tmp,
            'labelurl': '/gallery?searchType=' + 'ancient' + '&image=&label=on&query=' + tmp,
        } for tmp in label.split()]
    random.shuffle(labels)
    # data['labels'] = [{'label': x, 'labelurl': '/index'} for x in labels[:5]]
    data['labels'] = labels
    print(data)
    return data

# LANDING_DATA = get_landing_data()

# if __name__ == '__main__':
# print get_landing_data()['daily']
# print get_landing_data()['daily']
