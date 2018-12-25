# /usr/bin/env python
# -*- coding: utf-8 -*-

#以前的方法会被反爬，弃用
from sogou_translate import SogouTranslate, SogouLanguages
trans = SogouTranslate('999d9c1684fc8647cc25735e6b06c2e8', 'cdfb1d5759390db53254a2486f11da07')
#以上是我注册的账号，仅限内部使用
def en_to_zn_translate(content):
    return trans.translate(content,from_language=SogouLanguages.EN,to_language=SogouLanguages.ZH_CHS)

def zn_to_en_translate(content):
    return trans.translate(content,from_language=SogouLanguages.ZH_CHS,to_language=SogouLanguages.EN)
