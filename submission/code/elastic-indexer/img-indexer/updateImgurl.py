# coding:utf-8

import utils
import association
import codecs, json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import random

es = Elasticsearch(['localhost:9200'])
associator = association.Associator()


def process_img_results(res_tmp):
    res = []
    for item in res_tmp:
        item = item['_source']
        img = {}
        img['imgurl'] = item['imgurl']
        img['source'] = item['imgsrc']
        img['labels'] = item['asso']
        img['desc'] = item['desc']
        res.append(img)
    return res


def poem2img(poem='', cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    # 关键词分词，同义词扩展，返回assolist
    assolist = associator.assoAll(poem)
    try:
        assolist = assolist[:20]
    except:
        pass
    # 根据assolist搜索图片的asso
    search_body = {
        'query': {
            'match': {
                'asso': ' '.join(assolist)[:1000]
            }
        }
    }
    try:
        matches = es.count(index='imgasso', doc_type='imgasso_type', body=search_body)['count']
        search_body['from'] = (cur_page - 1) * pp
        search_body['size'] = pp
        res_tmp = es.search(index='imgasso', doc_type='imgasso_type', body=search_body)['hits']['hits']
    except Exception as e:
        print(e)
        return 0, []
    res = process_img_results(res_tmp)
    return matches, res


# 诗搜图
def giveimg2gishiwen():
    print('Give image to unmatched gushiwen...')
    i = 1
    for i in range(1, 22797 + 1):
        # 判断是否有图
        print('{}/{}'.format(i, 22797))
        search_body = {
            "query": {
                "ids": {
                    "type": "gushiwen_type",
                    "values": [i]
                }
            }
        }
        res = es.search(index='gushiwen', doc_type='gushiwen_type', body=search_body)['hits']['hits']
        try:
            poem = res[0]
        except:
            continue
        if poem['_source']['imgurl']:
            continue
        # 匹配图片
        matches, res = poem2img(poem['_source']['text_tokenized'])
        if len(res) == 0:
            continue
        imgurl = res[0]['imgurl']
        # 更新索引
        update_body = {
            'doc': {
                'imgurl': imgurl
            }
        }
        es.update(index='gushiwen', doc_type='gushiwen_type', id=i, body=update_body)


# 诗搜图
def giveimg2cnmodern():
    print('Give image to unmatched cnmodern...')
    i = 1
    for i in range(1, 5029):
        # 判断是否有图
        print('{}/{}'.format(i, 5029))
        search_body = {
            "query": {
                "ids": {
                    "type": "cnmodern_type",
                    "values": [i]
                }
            }
        }
        res = es.search(index='cnmodern', doc_type='cnmodern_type', body=search_body)['hits']['hits']
        try:
            poem = res[0]
        except:
            continue
        if poem['_source']['imgurl']:
            continue
        # 匹配图片
        matches, res = poem2img(poem['_source']['text_tokenized'])
        if len(res) == 0:
            continue
        imgurl = res[0]['imgurl']
        # 更新索引
        update_body = {
            'doc': {
                'imgurl': imgurl
            }
        }
        es.update(index='cnmodern', doc_type='cnmodern_type', id=i, body=update_body)


# 图搜诗
def giveimg2poem():
    print('Give image to all poems...')
    results = helpers.scan(
        client=es,
        query={'query': {'match_all': {}}},
        scroll='5m',
        index='imgasso',
        doc_type='imgasso_type',
        timeout='1m'
    )
    total = es.count(index='imgasso',
        doc_type='imgasso_type', body={'query': {'match_all': {}}})
    print(results)
    # input()
    cnt = 0
    for res in results:
        cnt += 1
        if cnt % 10 == 0:
            print('{}/{}'.format(cnt, total['count']))
        # 图片标签同义词古词拓展，返回assolist
        img = res
        assolist = img['_source']['asso']
        # 根据assolist搜索古诗的文本
        search_body = {
            'query': {
                'match': {
                    'text_tokenized': ' '.join(assolist)[:1000]
                }
            }
        }
        # 搜索结果数
        search_body['from'] = 0
        search_body['size'] = 5
        # 随机搜索古诗或现代诗
        if random.randint(0, 1):
            # 古诗
            # print('gushiwen')
            res = es.search(index='gushiwen', doc_type='gushiwen_type', body=search_body)['hits']['hits']
            for poem in res:
                if poem['_source']['imgurl']:
                    continue
                update_body = {
                    'doc': {
                        'imgurl': img['_source']['imgurl']
                    }
                }
                es.update(index='gushiwen', doc_type='gushiwen_type', id=poem['_id'], body=update_body)
                break
        else:
            # 现代诗
            # print('cnmodern')
            res = es.search(index='cnmodern', doc_type='cnmodern_type', body=search_body)['hits']['hits']
            for poem in res:
                if poem['_source']['imgurl']:
                    continue
                update_body = {
                    'doc': {
                        'imgurl': img['_source']['imgurl']
                    }
                }
                es.update(index='gushiwen', doc_type='gushiwen_type', id=poem['_id'], body=update_body)
                break
    giveimg2gishiwen()
    giveimg2cnmodern()


if __name__ == '__main__':
    # abandoned
    # giveimg2poem()

    giveimg2gishiwen()
    giveimg2cnmodern()
