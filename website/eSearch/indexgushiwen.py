

from elasticsearch import Elasticsearch
es = Elasticsearch()
result = es.search(index="my_index",doc_type="test_type")

# 或者这样写:搜索id=1的文档
result = es.get(index="my_index",doc_type="test_type",id=1)

print(result)
