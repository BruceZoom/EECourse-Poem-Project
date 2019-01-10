import json
import codecs
import pandas as pd
import numpy as np

with codecs.open('guci/myhotwords.dic', 'r', encoding='utf-8') as fin:
    words = [line.strip() for line in fin.readlines()]
    freq = pd.DataFrame({'words': words, 'freq': np.ones(len(words), dtype=int)}).set_index('words')
freq.to_csv('guci_dict.txt', sep=' ', encoding='utf-8', header=False)
