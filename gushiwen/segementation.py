import codecs
import jieba
import json


filename = 'data/gushiwen_basics.json'

with codecs.open(filename, 'r', encoding='utf-8') as f:
	data = json.loads(f.read())

print type(data[0]['song'])
for w in list(jieba.cut(data[0]['song'])):
	print w
