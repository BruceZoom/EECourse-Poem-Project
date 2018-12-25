# coding:utf-8
import lucene
from Index.modern_search import ModernPoemSearch
import utils

vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print 'vm initialized'

MPS = ModernPoemSearch('Index/modern_index')

"""
command_dict:
    key: field name
    value: (content, is accurate match)
"""

def common_query(input_dict, cur_page):
    if input_dict['searchType'] == "gushiwen":
        return shi_search(input_dict, cur_page)
    elif input_dict['searchType'] == "xiandaishi":
        return modern_search(input_dict, cur_page)
    elif input_dict['searchType'] == "all":
        return mixed_search(input_dict, cur_page)
    else:
        raise ValueError("Undefined Search Type")


def modern_search(input_dict, cur_page):
    pass

def shi_search(input_dict, cur_page):
    pass

def mixed_search(input_dict, cur_page):
    pass
