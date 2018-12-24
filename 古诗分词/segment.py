#! /usr/bin/env python3
#-*- coding:utf-8 -*-

import jieba

sxhy_path='sxhy_dict.txt'
class Segmenter(object):

    def __init__(self):
        with open(sxhy_path, 'r') as fin:
            self.sxhy_dict = set(fin.read().split())

    def segment(self, sentence):
        toks = []
        idx = 0
        while idx + 4 <= len(sentence):
            # 一次按两个字切
            if sentence[idx : idx + 2] in self.sxhy_dict:
                toks.append(sentence[idx : idx + 2])
            else:
                for tok in jieba.lcut(sentence[idx : idx + 2]):
                    toks.append(tok)
            idx += 2
        # 再切最后三个字
        if idx < len(sentence):
            if sentence[idx : ] in self.sxhy_dict:
                toks.append(sentence[idx : ])
            else:
                for tok in jieba.lcut(sentence[idx : ]):
                    toks.append(tok)
        return toks

if __name__ == '__main__':
    segmenter = Segmenter()
    sentence='仰天大笑出门去'
    print(' '.join(segmenter.segment(sentence)))

