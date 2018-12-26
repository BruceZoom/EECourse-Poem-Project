import jieba

MAX_RESULTS = 10000


def jieba_seg(str):
    try:
        return ' '.join(jieba.cut(str))
    except Exception, e:
        return str
