import jieba
import codecs
import json
import pandas as pd
import numpy as np

jieba.set_dictionary('guci_dict.txt')

with codecs.open('allpoems.json', 'r', encoding='utf-8') as fin:
    songs = json.load(fin)

freq = pd.read_csv('guci_dict.txt', sep=' ', names=['word', 'freq'], encoding='utf-8').set_index('word')
idf = pd.read_csv('guci_dict.txt', sep=' ', names=['word', 'idf'], encoding='utf-8').set_index('word')
freq.loc[:, 'freq'] = 1
idf = idf.drop(columns=['idf'])
idf.loc[:, 'idf'] = 0

cnt = 0
for song in songs:
    print('{}/{}'.format(cnt, len(songs)))
    cnt += 1
    ws = list(jieba.cut(song['text']))
    # print(list(ws))
    for w in ws:
        try:
            # print(0)
            freq.loc[w, 'freq'] += 1
        except:
            # print(1)
            # freq.loc[w, 'freq'] = 1
            continue
    # print(list(ws))
    ws = set(ws)
    # print(ws)
    for w in ws:
        try:
            # print(0)
            idf.loc[w, 'idf'] += 1
        except:
            # print(2)
            # idf.loc[w, 'idf'] = 1
            continue

idf.to_csv('guci_idf_org.txt', sep=' ', header=False, encoding='utf-8')

freq.loc[:, 'freq'] = freq.loc[:, 'freq'].astype(int)
idf.loc[:, 'idf'] = np.log(len(songs)/(idf.loc[:, 'idf'] + 1))
# idf.loc[:, 'idf'] = idf.loc[:, 'idf'].astype(int)

freq.to_csv('guci_dict.txt', sep=' ', header=False, encoding='utf-8')
idf.to_csv('guci_idf.txt', sep=' ', header=False, encoding='utf-8')

print(idf.loc[:, 'idf'].unique())
