# coding:utf-8

import utils
import association
import codecs, json
from elasticsearch import Elasticsearch
from PoemSearchES import process_query_results

es = Elasticsearch(['localhost:9200'])
associator = association.Associator()


def __get_item(d, k):
    if k not in d.keys() or d[k] is None:
        return ''
    else:
        return d[k]


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


def img2gushiwen(imglabels='', cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    # 图片标签同义词古词拓展，返回assolist
    assolist = associator.assoSynAll(imglabels)
    # 根据assolist搜索古诗的文本
    search_body = {
        'query': {
            'match': {
                'text_tokenized': ' '.join(assolist)
            }
        }
    }
    try:
        matches = es.count(index='gushiwen', doc_type='gushiwen_type', body=search_body)['count']
        search_body['from'] = (cur_page - 1) * pp
        search_body['size'] = pp
        res_tmp = es.search(index='gushiwen', doc_type='gushiwen_type', body=search_body)['hits']['hits']
    except Exception as e:
        print(e)
        return 0, []
    res = process_query_results(res_tmp, truncated)
    return matches, res

def img2cnmodern(imglabels='', cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    # 图片标签同义词古词拓展，返回assolist
    assolist = associator.assoSynAll(imglabels)
    # 根据assolist搜索古诗的文本
    search_body = {
        'query': {
            'match': {
                'text_tokenized': ' '.join(assolist)
            }
        }
    }
    try:
        matches = es.count(index='cnmodern', doc_type='cnmodern_type', body=search_body)['count']
        search_body['from'] = (cur_page - 1) * pp
        search_body['size'] = pp
        res_tmp = es.search(index='cnmodern', doc_type='cnmodern_type', body=search_body)['hits']['hits']
    except Exception as e:
        print(e)
        return 0, []
    res = process_query_results(res_tmp, truncated)
    return matches, res


def poem2img(poem='', cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    # 诗歌分词，抽出关键词（待实现）
    keywords = poem
    # 关键词分词，同义词扩展，返回assolist
    assolist = associator.assoAll(keywords)
    try:
        assolist = assolist[:20]
    except:
        pass
    # 根据assolist搜索图片的asso
    search_body = {
        'query': {
            'match': {
                'asso': ' '.join(assolist)
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
    # 处理返回图片(待实现)
    res = process_img_results(res_tmp)
    return matches, res


def giveimg2gishiwen():
    print('Give image to gushiwen...')
    with codecs.open('../sourcePoems/allpoems.json', 'r', encoding='utf-8') as fin:
        gushiwen = json.load(fin)
    i = 1
    for poem in gushiwen:
        # 匹配图片
        matches, res = poem2img(poem['title'] + poem['text'])
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
        i += 1

def giveimg2cnmodern():
    print('Give image to gushiwen...')
    with codecs.open('../sourcePoems/allchinesemoderns.json', 'r', encoding='utf-8') as fin:
        cnmodern = json.load(fin)
    i = 1
    for poem in cnmodern:
        # 匹配图片
        matches, res = poem2img(poem['title'] + poem['text'])
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
        i += 1


if __name__ == '__main__':
    # test poem2img
    # _, res = poem2img('星辰光影')
    # for i in res:
    #     print i

    # give img to gushiwen
    giveimg2cnmodern()
