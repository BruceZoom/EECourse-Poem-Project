# coding:utf-8
import codecs

DISPLAY_UTILS = {

}

FORM_INIT = {
    'searchType': 'all',
    'query': '',
    'image': '',
}

PAGI_INIT = {
    'offset': 3,
    'prev': '前一页',
    'next': '后一页',
    'top': '首页',
    'bottom': '尾页',
    'cur_page': 1,
    'max_page': 10,
    'result_per_page': 9,
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

UPLOAD_PREFIX = './static/upload/'
