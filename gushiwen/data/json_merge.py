import os
import json
import codecs

complete = []
root = 'gushiwen_complete/'
json_files = os.listdir(root)
for file in json_files:
	print file
	with codecs.open(root+file, 'r', encoding='utf-8') as f:
		data = json.loads(f.read())
		complete += data
with codecs.open('gushiwen_complete.json', 'w', encoding='utf-8') as f:
	json.dump(complete, f, indent=4, encoding='utf-8', ensure_ascii=False)
