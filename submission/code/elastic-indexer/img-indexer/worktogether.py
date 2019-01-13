# coding:utf-8
# 将本文件放在modern2poem下
# 将website中的translate.py拷贝一份到modern2poem下
# 在modern2poem文件夹内建立文件夹'myresult'
# '....my/dir/to/fengguang.json'位于sourcePoems/veer里

import json, codecs
import association
from translate import *
import os

with open('fengguang.json', 'r', encoding='utf-8')as fin:
    oneList = json.load(fin)

with open('labelDict.json', 'r', encoding='utf-8')as fin:
    label = json.load(fin)

associator = association.Associator()

myinitstart=0 #for dhy
# myinitstart=50000 # for chp
# myinitstart=100000 # for ljy
# myinitstart = 174003  # for wzy

myend=50000#for dhy
# myend=100000 for chp
# myend=150000 # for ljy
# myend = 198800  # for wzy


def working(mystart=myinitstart):
    Alllist = []
    for myitr in range(mystart, myend):
        dict = oneList[myitr]

        newdict = {}
        newdict['img'] = dict['imgurl']
        desc = dict['alt']

        try:
            print(1)
            chdesc = sg_en_to_zn_translate(desc)
            syns = associator.assoSynAll(chdesc)

            print(newdict['img'])
            print(desc)
            print(chdesc)
            print(syns)

            newdict['asso'] = syns
            newdict['desc'] = chdesc
        except:
            newdict['desc'] = desc
            newdict['asso'] = []
            print('woooooooooo')
            continue

        Alllist.append(newdict)

        if len(Alllist) % 1000 == 0:
            if not os.path.exists('myresult'):
                os.mkdir('myresult')
            with open('myresult/imgasso{}.json'.format(myitr + 1), 'w', encoding='utf-8') as f:
                json.dump(Alllist, f, ensure_ascii=False, indent=4)
            Alllist = []

    if len(Alllist) > 0:
        with open('myresult/imgasso{}.json'.format(myitr + 1), 'w', encoding='utf-8') as f:
            json.dump(Alllist, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    working()
