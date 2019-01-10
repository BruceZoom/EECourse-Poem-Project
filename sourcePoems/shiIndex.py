# coding=utf-8
import os, re
import json
import codecs
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import jieba
import jieba.analyse

index_analyzer = 'ik_max_word'
search_analyzer = 'ik_smart'


def _getkey(dict, key, seg=None, default=''):
    try:
        return dict[key]
    except:
        return default


def _genAllPoems():
    allPoems = []
    allAuthors = []
    _checkDict = {}

    def _alreadyIn(author, title):
        if author not in _checkDict.keys(): return False
        if title not in _checkDict[author]: return False
        return True

    print("-----collecting complete poems-----")
    with codecs.open('./gushiwen/gushiwen_complete.json', 'r', encoding='utf-8') as fin:  # 收集完全数据
        oneList = json.load(fin)

    for oneDict in oneList:
        newDict = {}
        info, newDict['likes'], extra, newDict['title'], content, label = _getkey(oneDict, "info"), _getkey(oneDict,
                                                                                                            "rating"), _getkey(
            oneDict, "extra"), _getkey(oneDict, "title"), _getkey(oneDict, "song"), _getkey(oneDict, "tags"),
        if info:
            dyn, newDict['author'] = info[0], info[1]
            if (dyn[0] == '宋'):
                if (len(set([len(x) for x in re.split('(\，|\。|\！|\!|\.|\？|\?|\（|\）|\(|\))', content[0]) if
                             len(x) > 1])) == 1):
                    newDict['dynasty'] = dyn[0] + '诗'
                else:
                    newDict['dynasty'] = dyn[0] + '词'
            elif (dyn[0] == '唐'):
                newDict['dynasty'] = "唐诗"
            else:
                newDict['dynasty'] = dyn
            try:
                _checkDict[newDict['author']].append(newDict['title'])
            except:
                _checkDict[newDict['author']] = [newDict['title']]
        if content: newDict["text"] = '\n'.join(content)
        if label: newDict['label'] = '\n'.join(label)
        zhushi, yiwen, shangxi = _getkey(extra, "zhushi"), _getkey(extra, "yiwen"), _getkey(extra, "shangxi"),
        if zhushi: newDict['zhushi'] = '\n'.join(zhushi)
        if yiwen: newDict['yiwen'] = '\n'.join(yiwen)
        if shangxi: newDict['shangxi'] = '\n'.join(shangxi)
        allPoems.append(newDict)

    print("-----collecting shi-----")
    for root, _, files in os.walk("./shi"):  # 收集基础诗
        for filename in files:
            if (os.path.join(root, filename).startswith('./shi/poet.song')):
                with codecs.open(os.path.join(root, filename), 'r', encoding='utf-8') as fin:
                    oneList = json.load(fin)
                for dict in oneList:
                    newdict = {}
                    if _alreadyIn(dict['author'], dict['title']):
                        continue
                    newdict['author'], newdict['title'] = dict['author'], dict['title']
                    newdict['text'] = '\n'.join(dict['paragraphs'])
                    newdict['dynasty'] = '宋诗'
                    allPoems.append(newdict)

            elif (os.path.join(root, filename).startswith('./shi/poet.tang')):
                with codecs.open(os.path.join(root, filename), 'r', encoding='utf-8') as fin:
                    oneList = json.load(fin)
                for dict in oneList:
                    newdict = {}
                    if _alreadyIn(dict['author'], dict['title']):
                        continue
                    newdict['author'], newdict['title'] = dict['author'], dict['title']
                    newdict['text'] = '\n'.join(dict['paragraphs'])
                    newdict['dynasty'] = '宋诗'
                    allPoems.append(newdict)

            else:  # 作者
                with codecs.open(os.path.join(root, filename), 'r', encoding='utf-8') as fin:
                    oneList = json.load(fin)
                allAuthors.extend(oneList)

    print("-----collecting ci-----")
    for itr in range(0, 21001, 1000):
        with codecs.open('./ci/ci.song.%d.json' % itr, 'r', encoding='utf-8') as fin:
            oneList = json.load(fin)
        for dict in oneList:
            if _alreadyIn(dict['author'], dict['rhythmic']): continue
            newdict = {}
            newdict['author'], newdict['title'] = dict['author'], dict['rhythmic']
            newdict['text'] = '\n'.join(dict['paragraphs'])
            newdict['dynasty'] = '宋词'
            allPoems.append(newdict)

    with codecs.open('./ci/author.song.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        allAuthors.append({'name': dict['name'], 'desc': dict["description"]})

    print("-----collecting shijing-----")
    with codecs.open('./shijing/shijing.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        newdict = {}
        newdict['text'] = '\n'.join(dict['content'])
        newdict['dynasty'] = '诗经'
        newdict['title'] = dict['title'] + '-' + dict['chapter'] + '-' + dict['section']
        allPoems.append(newdict)

    print("-----writing datas-----")
    with codecs.open('allpoems.json', 'w', encoding='utf-8') as f:
        json.dump(allPoems, f, ensure_ascii=False, indent=4)

    with codecs.open('allauthors.json', 'w', encoding='utf-8') as f:
        json.dump(allAuthors, f, ensure_ascii=False, indent=4)

    print("-----already generated-----")


def _genAllChineseModerns():
    AllChineseModerns = []
    with codecs.open('./modernPoems/cn_with_img.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    AllChineseModerns.extend(oneList)

    with codecs.open('./modernPoems/cn_with_img_trans.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        newdict = {}
        newdict['text'] = dict['poem']
        newdict['img'] = dict['image_url']
        AllChineseModerns.append(newdict)

    with codecs.open('./modernPoems/cn_without_img.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        newdict = {}
        newdict['text'] = dict['poem']
        newdict['author'] = dict['author']
        newdict['title'] = dict['title']
        AllChineseModerns.append(newdict)

    with codecs.open('allchinesemoderns.json', 'w', encoding='utf-8') as f:
        json.dump(AllChineseModerns, f, ensure_ascii=False, indent=4)


def _genAllEnglishModerns():
    AllEnglishModerns = []
    with codecs.open('./modernPoems/en_with_img.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        newdict = {}
        newdict['text'] = dict['poem']
        newdict['img'] = dict['image_url']
        AllEnglishModerns.append(newdict)

    with codecs.open('./modernPoems/en_without_img.json', 'r', encoding='utf-8') as fin:
        oneList = json.load(fin)
    for dict in oneList:
        newdict = {}
        newdict['text'] = dict['poem']
        AllEnglishModerns.append(newdict)

    with codecs.open('allenglishmoderns.json', 'w', encoding='utf-8') as f:
        json.dump(AllEnglishModerns, f, ensure_ascii=False, indent=4)


class GushiwenObj:
    def __init__(self, index_name='gushiwen', index_type='gushiwen_type'):
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self, index_name, index_type):
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "author": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "text_tokenized": {  # 分词、索引，但不独立储存，从_source中解析
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "text": {  # 储存完整的，以下按照同样逻辑
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "dynasty": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "imgurl": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "label_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": "whitespace",
                            "search_analyzer": "whitespace",
                        },
                        "label": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "shangxi_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "shangxi": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "title_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "title": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },

                        "yiwen_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "yiwen": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "zhushi_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "zhushi": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        }
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def bulk_Gushiwen_Data(self, list, seg=None):
        '''
        用bulk将批量的古诗数据存储到es
        '''
        ACTIONS = []
        i = 1
        for line in list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "author": _getkey(line, 'author'),
                    "text_tokenized": _getkey(line, 'text'),
                    "text": _getkey(line, 'text'),
                    "dynasty": _getkey(line, 'dynasty'),
                    "imgurl": _getkey(line, 'imgurl'),
                    "label_tokenized": _getkey(line, 'label'),
                    "label": _getkey(line, 'label'),
                    "shangxi_tokenized": _getkey(line, 'shangxi'),
                    "shangxi": _getkey(line, 'shangxi'),
                    "title_tokenized": _getkey(line, 'title'),
                    "title": _getkey(line, 'title'),
                    "yiwen_tokenized": _getkey(line, 'yiwen'),
                    "yiwen": _getkey(line, 'yiwen'),
                    "zhushi_tokenized": _getkey(line, 'zhushi'),
                    "zhushi": _getkey(line, 'zhushi'),
                }
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)


class AuthorObj:
    def __init__(self, index_name='author', index_type='author_type'):
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self, index_name, index_type):
        _index_mappings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ik": {
                            "tokenizer": "ik_max_word"
                        }
                    },
                }
            },
            "mappings": {
                self.index_type: {
                    "properties": {
                        "name": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "desc_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "analyzer": "ik_max_word",
                            # "search_analyzer": search_analyzer,
                        },
                        "desc": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "genre": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "time_key": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "time_text": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "type": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        }
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def bulk_Author_Data(self, ancient_list,modern_list, seg=jieba.cut):
        ACTIONS = []
        i = 1

        for line in modern_list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "name": _getkey(line, 'author'),
                    "desc_tokenized": "",
                    "desc": "",
                    "genre":_getkey(line, 'genre'),
                    "time_key":_getkey(line, 'time_key'),
                    "time_text":_getkey(line, 'time_text'),
                    "type":"modern"
                }
            }
            i += 1
            ACTIONS.append(action)

        for line in ancient_list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "name": _getkey(line, 'name'),
                    "desc_tokenized": _getkey(line, 'desc'),
                    "desc": _getkey(line, 'desc'),
                    "genre":"",
                    "time_key":"",
                    "time_text":"",
                    "type":"ancient"
                }
            }
            i += 1
            ACTIONS.append(action)

            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)


class ChineseModernsObj:
    def __init__(self, index_name='cnmodern', index_type='cnmodern_type'):
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self, index_name, index_type):
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "author": {
                            "type": "text",
                            "index": True,
                            "store": True,
                            "analyzer": "whitespace",
                            "search_analyzer": "whitespace",
                        },
                        "text_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "text": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "label_tokenized": {
                            "type": "keyword",
                            "index": True,
                            "store": False,
                            "index_analyzer": "whitespace",
                            "search_analyzer": "whitespace",
                        },
                        "label": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "title_tokenized": {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        "title": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "imgurl": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        'genre_text': {
                            "type": "text",
                            "index": True,
                            "store": False,
                            "index_analyzer": index_analyzer,
                            "search_analyzer": search_analyzer,
                        },
                        'genre_key': {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        'time_text': {
                            "type": "text",
                            "index": False,
                            "store": False,
                        },
                        'time_key': {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        }
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def bulk_ChineseModerns_Data(self, list, authorInfo, seg=jieba.cut):
        ACTIONS = []
        i = 1
        for line in list:
            author = _getkey(line, 'author')
            labels = ' '.join(jieba.analyse.extract_tags(_getkey(line, 'text'), topK=5, withWeight=False))
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "author": _getkey(line, 'author'),
                    "text_tokenized": _getkey(line, 'text'),
                    "text": _getkey(line, 'text'),
                    "title_tokenized": _getkey(line, 'title'),
                    "title": _getkey(line, 'title'),
                    "imgurl": _getkey(line, 'img'),
                    "label_tokenized": labels,
                    "label": labels,
                    "genre_text": _getkey(_getkey(authorInfo, author), 'genre', default='无'),
                    "genre_key": _getkey(_getkey(authorInfo, author), 'genre', default='无'),
                    "time_text": _getkey(_getkey(authorInfo, author), 'time_text', default='无'),
                    "time_key": _getkey(_getkey(authorInfo, author), 'time_key', default='无'),
                }
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)


class EnglishModernsObj:
    def __init__(self, index_name='enmodern', index_type='enmodern_type'):
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch()

    def create_index(self, index_name, index_type):
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "text_tokenized": {
                            "type": "text",
                            "index": True,
                            "analyzer": "english"
                        },
                        "text": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                        "imgurl": {
                            "type": "keyword",
                            "index": "not_analyzed",
                            "store": True,
                        },
                    }
                }
            }
        }

        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def bulk_EnglishModerns_Data(self, list):
        ACTIONS = []
        i = 1
        for line in list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i,
                "_source": {
                    "text_tokenized": _getkey(line, 'text'),
                    "text": _getkey(line, 'text'),
                    "imgurl": _getkey(line, 'img'),
                }
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)


if __name__ == '__main__':
    # ---先生成总的诗数据，用一次后请注释掉---

    # _genAllPoems()
    # _genAllChineseModerns()
    # _genAllEnglishModerns()

    # ---生成总数据---

    # ---建立索引，用一次后请注释掉---
    # obj = GushiwenObj()
    # print('indexing gushiwen...')
    # with codecs.open('allpoems.json', 'r', encoding='utf-8')as fin:
    #     poemList = json.load(fin)
    # obj.bulk_Gushiwen_Data(poemList)
    # del poemList

    obj = AuthorObj()
    print('indexing authors...')
    with codecs.open('allauthors.json', 'r', encoding='utf-8') as fin:
        ancientList = json.load(fin)
    with codecs.open('cnmodern_author_info.json', 'r', encoding='utf-8') as fin:
        modernList = json.load(fin)
    obj.bulk_Author_Data(ancientList,modernList)
    del ancientList
    del modernList

    # obj = ChineseModernsObj()
    # print('indexing chinese moderns...')
    # with codecs.open('allchinesemoderns.json', 'r', encoding='utf-8') as fin:
    #     poemList = json.load(fin)
    # with codecs.open('cnmodern_author_info.json', 'r', encoding='utf-8') as fin:
    #     authorInfo = json.load(fin)
    # obj.bulk_ChineseModerns_Data(poemList, authorInfo)
    # del poemList
    # del authorInfo

    #
    # obj = EnglishModernsObj()
    # print('indexing english moderns...')
    # with codecs.open('allenglishmoderns.json', 'r', encoding='utf-8') as fin:
    #     poemList = json.load(fin)
    # obj.bulk_EnglishModerns_Data(poemList)
    # del poemList
    # ---建立索引---

    # TODO: 继续丰富上面几个类的内容，完善搜索、增删改查的功能
