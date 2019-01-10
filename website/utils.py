# coding:utf-8
import codecs
import os
import jieba
import homeContent

DISPLAY_UTILS = {
    'card_max_text': 50,
}

FORM_INIT = {
    'searchType': 'all',
    'query': '',
    'image': '',
}

PAGI_SETTING = {
    'offset': 3,
    'prev': '前一页',
    'next': '后一页',
    'top': '首页',
    'bottom': '尾页',
    'cur_page': 1,
    'max_page': 10,
    'result_per_page': 9,
}
LANDING_DATA = homeContent.get_landing_data()
LANDING_DATA_DEFAULT = {
    'daily': {
        'title': 'Title',
        'imgurl': '/static/image/1.jpg',
        'content': "这是一首每日推荐 这是一首每日推荐 这是一首每日推荐 这是一首每日推荐",
        'poet': 'Someone famous in My memories',
        'poemurl': '/index',
        'poeturl': '/index',
    },
    'random_modern': [
        {
            'title': 'Title',
            'content': '我是一首现代诗 我是一首现代诗 我是一首现代诗 我是一首现代诗 ',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
        {
            'title': 'Title',
            'content': '我是一首现代诗 我是一首现代诗 我是一首现代诗 我是一首现代诗',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
        {
            'title': 'Title',
            'content': '我是一首现代诗 我是一首现代诗 我是一首现代诗 我是一首现代诗',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
    ],
    'scenery': {
        'title': 'Title',
        'imgurl': '/static/image/1.jpg',
        'content': "这是一首每日推荐 这是一首每日推荐 这是一首每日推荐 这是一首每日推荐",
        'poet': 'Someone famous in My memories',
        'poemurl': '/index',
        'poeturl': '/index',
    },
    'random_ancient': [
        {
            'title': 'Title',
            'content': '我是一首古诗 我是一首古诗 我是一首古诗 我是一首古诗 ',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
        {
            'title': 'Title',
            'content': '我是一首古诗 我是一首古诗 我是一首古诗 我是一首古诗',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
        {
            'title': 'Title',
            'content': '我是一首古诗 我是一首古诗 我是一首古诗 我是一首古诗',
            'poet': 'Someone famous in My memories',
            'poemurl': '/index',
            'poeturl': '/index',
        },
    ],
    'daily_ancient': {
        'title': 'Title',
        'content': "这是一首每日推荐 这是一首每日推荐 这是一首每日推荐 这是一首每日推荐",
        'poet': 'Someone famous in My memories',
        'poemurl': '/index',
        'poeturl': '/index',
    },
    'labels': [
        {
            'label': '标签标签标签',
            'labelurl': '#',
        },
        {
            'label': '标签',
            'labelurl': '#',
        },
        {
            'label': '标签标签',
            'labelurl': '#',
        },
        {
            'label': '标签',
            'labelurl': '#',
        },
        {
            'label': '标签标签',
            'labelurl': '#',
        },
    ],
}

ENTRY_TEMPLATE = {
    'imgurl': '/static/image/1.jpg',
    'title': 'Title',
    'content': '我是一首诗 我是一首诗 我是一首诗 我是一首诗',
    'poet': '诗人',
    'poemurl': '#',
    'poeturl': '#',
    'labels': [
        # {
        #     'label': '标签',
        #     'labelurl': '#',
        # },
    ],
    'likes': 0,
}

ENTRY_SAMPLES = [
    {
        'imgurl': '/static/image/1.jpg',
        'title': 'Title',
        'content': '我是一首诗 我是一首诗 我是一首诗 我是一首诗',
        'poet': '诗人',
        'poemurl': '#',
        'poeturl': '#',
        'labels': [
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
        ],
        'likes': 321,
    },
    {
        'imgurl': '/static/image/1.jpg',
        'title': 'Title',
        'content': '我是一首诗 我是一首诗 我是一首诗 我是一首诗',
        'poet': '诗人',
        'poemurl': '#',
        'poeturl': '#',
        'labels': [
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
        ],
        'likes': 321,
    },
    {
        'imgurl': '/static/image/1.jpg',
        'title': 'Title',
        'content': '我是一首诗 我是一首诗 我是一首诗 我是一首诗',
        'poet': '诗人',
        'poemurl': '#',
        'poeturl': '#',
        'labels': [
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
            {
                'label': '标签',
                'labelurl': '#',
            },
        ],
        'likes': 321,
    },
]

with codecs.open('templates/header.html', 'r', encoding='utf-8') as f:
    HEADER = ''.join(f.readlines())

with codecs.open('templates/footer.html', 'r', encoding='utf-8') as f:
    FOOTER = ''.join(f.readlines())

timestamp = len([lists for lists in os.listdir('./static/upload/')])

UPLOAD_PREFIX = './static/upload/'
RELU_PREFIX = './static/relu/'

def alternating(a1, a2):
    res = a2[:]
    for i in range(len(a1)):
        res.insert(2 * i, a1[i])
    return res


def jieba_seg(str):
    try:
        return ' '.join(jieba.cut(str))
    except:
        return str
