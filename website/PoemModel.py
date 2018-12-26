# coding:utf-8
import lucene
from Index.modern_search import ModernPoemSearcher
from Index.ancient_search import AncientPoemSearcher
import utils

vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print 'vm initialized'

MPS = ModernPoemSearcher('Index/modern_index')
APS = AncientPoemSearcher('Index/gushiwen_index')

"""
command_dict:
    key: field name
    value: (content, is accurate match)
"""


def common_query(input_dict, cur_page=1):
    if input_dict['searchType'] == "ancient":
        return shi_search(input_dict, cur_page)
    elif input_dict['searchType'] == "modern":
        return modern_search(input_dict, cur_page)
    elif input_dict['searchType'] == "all":
        return mixed_search(input_dict, cur_page)
    else:
        raise ValueError("Undefined Search Type")


def modern_search(input_dict, cur_page=1):
    pass


def shi_search(input_dict, cur_page=1):
    pass


def mixed_search(input_dict, cur_page=1):
    pass
