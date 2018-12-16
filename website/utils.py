# coding:utf-8
import codecs

DISPLAY_UTILS = {

}

FORM_INIT = {
    'searchType': 'all',
    'query': '',
}

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
}

with codecs.open('templates/header.html', 'r', encoding='utf-8') as f:
    HEADER = ''.join(f.readlines())
