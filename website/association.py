#-*- coding:utf-8 -*-

import jieba
import os,codecs
import json
from random import random
import synonyms
# 若还需要英文信息，进入transLists.zip
# 若要运行_gen_asso_dict()，进入transLists.zip

def _gen_asso_dict():
    assoDict={}

    for itr in range(2,328):
        with open("transList%d.json"%itr,'r') as fin:
            print("-----parsing transList%d.json------"%itr)
            storeData=json.load(fin)

        for valueList in storeData.values():
            ch,chMeaning,modernList=valueList[0],valueList[2],valueList[3]
            if not modernList:#现代汉语近义词集为空
                assoDict[chMeaning]=[(ch,0)]
            else:
                totalLen=len(modernList)
                for i in range(totalLen):
                    modernCh=modernList[i]
                    ind=int(i/totalLen*10)#归一化到1,2,..10的权值，越小越相关
                    if modernCh not in assoDict:
                        assoDict[modernCh]=[(ch,ind)]
                    else:
                        assoDict[modernCh].append((ch,ind))
        print("len of assoDict is %d now"%len(assoDict))

    stnum=1
    for key,value in assoDict.items():
        value=sorted(value,key=lambda x:x[1])#越小的越相关
        assoDict[key]=value
        stnum+=1
        if(stnum%200==0):print("sorting %d-th word"%stnum)

    with codecs.open("assoDict.json",'w')as f:
        json.dump(assoDict,f,ensure_ascii=False,indent=4)


class Associator(object):

    def __init__(self):
        if not os.path.exists("assoDict.json"):
            _gen_asso_dict()

        with open("assoDict.json",'r') as fin:
            self.assoDict=json.load(fin)

    def assoAll(self,sentence):
        # sentence: 中文句/词
        # 找到所有的关联古词，按照相关性顺序返回list
        toks=jieba.lcut(sentence)
        assoRes=[]
        for word in toks:
            try:assoRes.extend(self.assoDict[word])
            except:continue
        assoRes=sorted(assoRes,key=lambda x:x[1])
        assoRes=[x[0] for x in assoRes]
        finalRes=list(set(assoRes))
        finalRes.sort(key=assoRes.index)
        return finalRes

    def assoRandom(self,sentence,assoLen=5):
        # sentence: 中文句/词
        # assoLen: 返回联想词的最多个数
        # 按照加权随机的方法返回前assoLen个词
        toks=jieba.lcut(sentence)
        assoRes=[]
        for word in toks:
            try:assoRes.extend(self.assoDict[word])
            except:continue
        assoRes=sorted(assoRes,key=lambda x:x[1]*random())
        assoRes=[x[0] for x in assoRes]
        finalRes=list(set(assoRes))
        finalRes.sort(key=assoRes.index)
        return finalRes[:assoLen]

    def assoSynAll(self,sentence):
        # sentence: 中文句/词,并且对这些词先找近义词，再分别找古词
        # 找到前五个近义词的所有关联古词，按照相关性顺序返回list
        # 计算量或许有点大
        toks=jieba.lcut(sentence)
        assoRes=[]
        synWords=[]
        for word in toks:
            synlist,score=synonyms.nearby(word)
            synlist,score=synlist[:5],score[:5]
            synWords.extend(zip(synlist,score))
        # print(synWords)
        for synword in synWords:
            try:
                synwordList=self.assoDict[synword[0]]
                synwordList=[(x[0],x[1]*(1.1-synword[1])) for x in synwordList]#因为synonyms库中，越大越近
                assoRes.extend(synwordList)
            except:continue
        assoRes=sorted(assoRes,key=lambda x:x[1])
        assoRes=[x[0] for x in assoRes]
        finalRes=list(set(assoRes))
        finalRes.sort(key=assoRes.index)
        return finalRes

    # TODO:将这部分内容转移到搜索的索引中，可以通过搜现代汉语得到联想的古词意象，进而搜索诗句
    # TODO:加速的方法，比如直接搜词，不再分词

# For testing purpose.
if __name__ == '__main__':

    associator=Associator()
    while(1):
        str=input("请输入现代汉语：")
        print(' '.join(associator.assoAll(str)))



