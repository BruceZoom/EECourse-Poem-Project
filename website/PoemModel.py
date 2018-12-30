# coding:utf-8
import lucene
from Index.modern_search import ModernPoemSearcher
from Index.ancient_search import AncientPoemSearcher
import utils

vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print ('vm initialized')

MPS = ModernPoemSearcher('Index/modern_index')
APS = AncientPoemSearcher('Index/gushiwen_index')

"""
command_dict:
    key: field name
    value: (content, is accurate match)
"""


def alternating(a1, a2):
    res = a2[:]
    for i in range(len(a1)):
        res.insert(2*i, a1[i])
    return res


def common_query(input_dict, cur_page=1):
    vm_env.attachCurrentThread()
    if input_dict['searchType'] == "ancient":
        return ancient_search(input_dict, cur_page)
    elif input_dict['searchType'] == "modern":
        return modern_search(input_dict, cur_page)
    elif input_dict['searchType'] == "all":
        return mixed_search(input_dict, cur_page)
    else:
        raise ValueError("Undefined Search Type")

# ENTRY_TEMPLATE = {
#         'imgurl': '/static/image/1.jpg',
#         'title': 'Title',
#         'content': '我是一首诗 我是一首诗 我是一首诗 我是一首诗',
#         'poet': '诗人',
#         'poemurl': '#',
#         'poeturl': '#',
#         'labels': [
#             # {
#             #     'label': '标签',
#             #     'labelurl': '#',
#             # },
#         ],
#         'likes': 0,
# }


def modern_search(input_dict, cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    matches, res_tmp = MPS.ch_seach(input_dict, target_range=((cur_page-1)*pp, cur_page*pp))
    res = []
    for tmp in res_tmp:
        if tmp['imgurl'] == '':
            tmp['imgurl'] = '/static/image/1.jpg'
        if truncated and len(tmp['text']) > utils.DISPLAY_UTILS['card_max_text']:
            tmp['text'] = tmp['text'][:utils.DISPLAY_UTILS['card_max_text']] + '...'
        entry = {
            'imgurl': tmp['imgurl'],
            'title': tmp['title'],
            'content': tmp['text'],
            'poet': tmp['author'],
            'poemurl': '#',
            'poeturl': '#',
            'labels': [
                {
                    'label': label,
                    'labelurl': '#',
                }
                for label in tmp['label'].split()],
            'likes': 0,
        }
        res.append(entry)
    return matches, res


def ancient_search(input_dict, cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    matches, res_tmp = APS.gushiwen_search(input_dict, target_range=((cur_page - 1) * pp, cur_page * pp))
    # print matches, res_tmp
    res = []
    for tmp in res_tmp:
        if tmp['imgurl'] == '':
            tmp['imgurl'] = '/static/image/1.jpg'
        if truncated and len(tmp['text']) > utils.DISPLAY_UTILS['card_max_text']:
            tmp['text'] = tmp['text'][:utils.DISPLAY_UTILS['card_max_text']] + '...'
        entry = {
            'imgurl': tmp['imgurl'],
            'title': tmp['title'],
            'content': tmp['text'],
            'poet': tmp['author'],
            'poemurl': '#',
            'poeturl': '#',
            'labels': [
                {
                    'label': label,
                    'labelurl': '#',
                }
                for label in tmp['label'].split()],
            'likes': 0,
        }
        res.append(entry)
    return matches, res


def mixed_search(input_dict, cur_page=1, pp=utils.PAGI_SETTING['result_per_page'], truncated=True):
    matches_modern, res_modern = modern_search(input_dict, cur_page, pp//2, truncated)
    matches_ancient, res_ancient = ancient_search(input_dict, cur_page, pp//2, truncated)
    res = alternating(res_modern, res_ancient)
    matches = matches_modern + matches_ancient
    return matches, res
