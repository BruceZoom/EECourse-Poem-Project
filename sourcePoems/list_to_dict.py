import json
import codecs

filename = 'cnmodern_author_info.json'
key = 'author'

with codecs.open(filename, 'r', encoding='utf-8') as fin:
    l = json.load(fin)
d = {}
for i in range(len(l)):
    d[l[i][key]] = l[i]
    print('{}/{}'.format(i, len(l)))
with codecs.open(filename, 'w', encoding='utf-8') as fout:
    json.dump(d, fout, ensure_ascii=False, indent=4)
