# /usr/bin/env python
# -*- coding: utf-8 -*-
# /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.parse
import execjs,requests
import random

ua='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
class Return_tk():
    def __init__(self):
        self.ctx = execjs.compile("""
        function TL(a) {
        var k = "";
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };

    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
    """)
    def getTk(self, text):
        return self.ctx.call("TL", text)

def open_url(url):
    headers = {'User-Agent': ua}
    req = requests.get(url=url, headers=headers)
    return req.content.decode('utf-8')

def en_to_zn_translate(content):
    '''
    Parameters
    ----------
    content : str

    Returns
    -------
    str
        translated content
    '''
    js = Return_tk()
    tk = js.getTk(content)
    numOfLines=content.count('\n')+1
    content = urllib.parse.quote(content)
    #英译汉
    url = "http://translate.google.cn/translate_a/single?client=t" \
          "&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
          "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1" \
          "&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)
    result = open_url(url)[4:]
    finalRes=""
    list=result.split('],["')
    for i in range(numOfLines):
        rawLine=list[i]
        str_end = rawLine.find("\",\"")
        finalRes+=rawLine[:str_end]
    return finalRes

def zn_to_en_translate(content):
    '''
    Parameters
    ----------
    content : str

    Returns
    -------
    str
        translated content
    '''
    js = Return_tk()
    tk = js.getTk(content)
    numOfLines=content.count('\n')+1
    content = urllib.parse.quote(content)
    #汉译英
    url = "http://translate.google.cn/translate_a/single?client=t"\
          "&sl=zh-CN&tl=en&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca"\
          "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8"\
          "&source=btn&ssel=3&tsel=3&kc=0&tk=%s&q=%s"%(tk,content)
    result = open_url(url)[4:]
    finalRes=""
    list=result.split('],["')
    for i in range(numOfLines):
        rawLine=list[i]
        str_end = rawLine.find("\",\"")
        finalRes+=rawLine[:str_end]
    return finalRes

'''
#以前的方法会被反爬，弃用（但似乎谷歌效果更好一点）
#因此，爬大量数据用这个，一般用外面的谷歌
from sogou_translate import SogouTranslate, SogouLanguages
trans = SogouTranslate('999d9c1684fc8647cc25735e6b06c2e8', 'cdfb1d5759390db53254a2486f11da07')
#以上是我注册的账号，仅限内部使用
def en_to_zn_translate(content):
    return trans.translate(content,from_language=SogouLanguages.EN,to_language=SogouLanguages.ZH_CHS)

def zn_to_en_translate(content):
    return trans.translate(content,from_language=SogouLanguages.ZH_CHS,to_language=SogouLanguages.EN)
'''
