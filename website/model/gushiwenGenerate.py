# coding:utf-8

import tensorflow as tf
import numpy as np
import argparse
import os
import random
import time
import collections

batchSize = 64
learningRateBase = 0.001
learningRateDecayStep = 1000
learningRateDecayRate = 0.95

epochNum = 10                    # train epoch
generateNum = 5                   # number of generated poems per time

type = "poetrySong"                   # dataset to use, shijing, songci, etc

trainPoems = "/Users/markdana/Desktop/EECourse-Poem-Project/website/model/gushiwenModel/datasets/" + type + ".txt" # training file location
checkpointsPath = "/Users/markdana/Desktop/EECourse-Poem-Project/website/model/gushiwenModel/checkpoints/" + type # checkpoints location
_pinyin_path="/Users/markdana/Desktop/EECourse-Poem-Project/website/model/gushiwenModel/datasets/pinyin.txt" # get pron dict
meta_graph="/Users/markdana/Desktop/EECourse-Poem-Project/website/model/gushiwenModel/checkpoints/" + type + '/poetrySong-236999.meta' # checkpoints location

saveStep = 1000                   # save model every savestep
trainRatio = 0.8                    # train percentage
evaluateCheckpointsPath = "/Users/markdana/Desktop/EECourse-Poem-Project/website/model/gushiwenModel/checkpoints/evaluate"

def _get_vowel(pinyin):
    i = 0
    while i < len(pinyin) and \
            pinyin[i] not in ['A', 'O', 'E', 'I', 'U', 'V']:
        i += 1
    return pinyin[i : ]

def _get_rhyme(pinyin):
    vowel = _get_vowel(pinyin)
    if vowel in ['A', 'IA', 'UA']:
        return 1
    elif vowel in ['O', 'E', 'UO']:
        return 2
    elif vowel in ['IE', 'VE']:
        return 3
    elif vowel in ['AI', 'UAI']:
        return 4
    elif vowel in ['EI', 'UI']:
        return 5
    elif vowel in ['AO', 'IAO']:
        return 6
    elif vowel in ['OU', 'IU']:
        return 7
    elif vowel in ['AN', 'IAN', 'UAN', 'VAN']:
        return 8
    elif vowel in ['EN', 'IN', 'UN', 'VN']:
        return 9
    elif vowel in ['ANG', 'IANG', 'UANG']:
        return 10
    elif vowel in ['ENG', 'ING']:
        return 11
    elif vowel in ['ONG', 'IONG']:
        return 12
    elif (vowel == 'I' and not pinyin[0] in ['Z', 'C', 'S', 'R']) \
            or vowel == 'V':
        return 13
    elif vowel == 'I':
        return 14
    elif vowel == 'U':
        return 15
    return 0

class PronDict(object):

    def __init__(self):
        self._pron_dict = dict()
        with open(_pinyin_path, 'r') as fin:
            for line in fin.readlines():
                toks = line.strip().split()
                ch = chr(int(toks[0], 16))
                self._pron_dict[ch] = []
                for tok in toks[1 : ]:
                    self._pron_dict[ch].append((tok[:-1], int(tok[-1])))

    def co_rhyme(self, a, b):
        """ Return True if two pinyins may have the same rhyme. """
        if a in self._pron_dict and b in self._pron_dict:
            a_rhymes = map(lambda x : _get_rhyme(x[0]), self._pron_dict[a])
            b_rhymes = map(lambda x : _get_rhyme(x[0]), self._pron_dict[b])
            for a_rhyme in a_rhymes:
                if a_rhyme in b_rhymes:
                    return True
        return False

    def counter_tone(self, a, b):
        """ Return True if two pinyins may have opposite tones. """
        if a in self._pron_dict and b in self._pron_dict:
            level_tone = lambda x : x == 1 or x == 2
            a_tones = map(lambda x : level_tone(x[1]), self._pron_dict[a])
            b_tones = map(lambda x : level_tone(x[1]), self._pron_dict[b])
            for a_tone in a_tones:
                if (not a_tone) in b_tones:
                    return True
        return False

    def __iter__(self):
        return iter(self._pron_dict)

    def __getitem__(self, ch):
        return self._pron_dict[ch]

class POEMS:
    def __init__(self, filename, isEvaluate=False):
        """pretreatment"""
        self.pronDict=PronDict()
        poems = []
        file = open(filename, "r")
        for line in file:  #every line is a poem
            title, author, poem = line.strip().split("::")  #get title and poem
            poem = poem.replace(' ','')
            if len(poem) < 10 or len(poem) > 512:  #filter poem
                continue
            if '_' in poem or '《' in poem or '[' in poem or '(' in poem or '（' in poem:
                continue
            poem = '[' + poem + ']' #add start and end signs
            poems.append(poem)

        #counting words
        wordFreq = collections.Counter()
        for poem in poems:
            wordFreq.update(poem)

        wordFreq[" "] = -1
        wordPairs = sorted(wordFreq.items(), key = lambda x: -x[1])
        self.words, freq = zip(*wordPairs)
        self.wordNum = len(self.words)

        self.wordToID = dict(zip(self.words, range(self.wordNum))) #word to ID
        poemsVector = [([self.wordToID[word] for word in poem]) for poem in poems] # poem to vector
        if isEvaluate: #evaluating need divide dataset into test set and train set
            self.trainVector = poemsVector[:int(len(poemsVector) * trainRatio)]
            self.testVector = poemsVector[int(len(poemsVector) * trainRatio):]
        else:
            self.trainVector = poemsVector
            self.testVector = []

class GushiwenGenerator(object):

    def __init__(self, trainData):
        self.trainData = trainData
        self.graph = tf.Graph()  # create a new graph

        with self.graph.as_default():
            self.gtX = tf.placeholder(tf.int32, shape=[1, None])  # input
            self.logits, self.probs, self.stackCell, self.initState, self.finalState = self.buildModel(self.trainData.wordNum, self.gtX)

        self.sess = tf.Session(graph=self.graph)  # 创建新的sess
        with self.sess.graph.as_default():
            self.sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()
            checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
            print("restoring %s" % checkPoint.model_checkpoint_path)
            saver.restore(self.sess, checkPoint.model_checkpoint_path)
            print("restored %s" % checkPoint.model_checkpoint_path)

    def buildModel(self, wordNum, gtX, hidden_units=128, layers=2):
        with tf.variable_scope("embedding"):  # embedding
            embedding = tf.get_variable("embedding", [wordNum, hidden_units], dtype=tf.float32)
            inputbatch = tf.nn.embedding_lookup(embedding, gtX)

        basicCell = tf.contrib.rnn.BasicLSTMCell(hidden_units, state_is_tuple=True)
        stackCell = tf.contrib.rnn.MultiRNNCell([basicCell] * layers)
        initState = stackCell.zero_state(np.shape(gtX)[0], tf.float32)
        outputs, finalState = tf.nn.dynamic_rnn(stackCell, inputbatch, initial_state=initState)
        outputs = tf.reshape(outputs, [-1, hidden_units])

        with tf.variable_scope("softmax"):
            w = tf.get_variable("w", [hidden_units, wordNum])
            b = tf.get_variable("b", [wordNum])
            logits = tf.matmul(outputs, w) + b

        probs = tf.nn.softmax(logits)
        return logits, probs, stackCell, initState, finalState

    def probsToWord(self, weights, poemnow, prondict, words):
        num_per_sen = poemnow.find('，')
        used_chars = set(ch for ch in poemnow)
        idx = len(poemnow)
        for i in range(len(weights[0])):
            ch = words[i]
            if ch in used_chars:
                weights[0][i] *= 0.6  # 防止过多叠词，目前还学不到凄凄惨惨戚戚的程度

            if num_per_sen > 1:  # 第一句已经做出来了
                if ((idx - num_per_sen + 1) / (num_per_sen + 1)) % 2 == 1 and \
                        not prondict.co_rhyme(ch, poemnow[num_per_sen - 1]):
                    weights[0][i] *= 0.001  # 一三五不论，二四六分明

                counterind = idx % (num_per_sen + 1)
                if 1 == counterind and \
                        not prondict.counter_tone(poemnow[1], ch):
                    weights[0][i] *= 0.4  # 平仄
                if counterind > 1 and counterind % 2 == 1 and \
                        not prondict.counter_tone(poemnow[idx - 1], ch):
                    weights[0][i] *= 0.4

        prefixSum = np.cumsum(weights)  # 按概率随机抽取
        ratio = np.random.rand(1)
        index = np.searchsorted(prefixSum, ratio * prefixSum[-1])  # large margin has high possibility to be sampled
        return words[index[0]]


    def genfromKeywords(self,keywords):
        """
        从sxhy古词生成古诗，keywords长度至少为4（通过前面拓展）
        :param keywords:list，其中词应该全部来源于sxhy,通过在上一步设置用户选择框得到
        :return:
        """

        with self.sess.graph.as_default():
            state = self.sess.run(self.stackCell.zero_state(1, tf.float32))
            x = np.array([[self.trainData.wordToID['[']]])
            probs1, state = self.sess.run([self.probs, self.finalState], feed_dict={self.gtX: x, self.initState: state})


            flag = 1
            endSign = {-1: "，", 1: "。"}
            poem = ''
            poemList=[]

            poemLen=len(keywords)//4*4
            keywords=random.sample(keywords,poemLen)

            for word in keywords:
                flag = -flag
                wordlasting = len(word)
                while word not in [']', '，', '。', ' ', '？', '！']:
                    if wordlasting>=1: thisword=word[len(word)-wordlasting]
                    else: thisword=word

                    poem += thisword
                    try:thisid=self.trainData.wordToID[thisword]
                    except:thisid=self.trainData.wordToID['不']

                    x = np.array([[thisid]])
                    probs2, state = self.sess.run([self.probs, self.finalState], feed_dict={self.gtX: x, self.initState: state})
                    if wordlasting >= 2:
                        wordlasting -= 1

                    else:
                        word = self.probsToWord(probs2,poem,self.trainData.pronDict,self.trainData.words)
                        wordlasting=0

                poem += endSign[flag]

                if endSign[flag] == '。':
                    probs2, state = self.sess.run([self.probs, self.finalState],
                                             feed_dict={self.gtX: np.array([[self.trainData.wordToID["。"]]]), self.initState: state})
                    # poem += '\n'
                    if(len(poemList)==0):
                        poemList.append(poem)
                    else:
                        onestr=poem[-1*len(poemList[0]):]
                        if onestr[0]=='。':
                            poemList.append(onestr[1:])
                        else:
                            poemList.append(onestr)
                else:
                    probs2, state = self.sess.run([self.probs, self.finalState],
                                             feed_dict={self.gtX: np.array([[self.trainData.wordToID["，"]]]), self.initState: state})

            return poemList


    # def genfromSentence(self,sentence):
    #     """
    #
    #     :param sentence: 一个汉语句子即可
    #     :return:
    #     """
    #     keywords=self.associator.assoRandom(sentence,assoLen=8)
    #     return self.genfromKeywords(keywords)
        
trainData = POEMS(trainPoems)
gsw=GushiwenGenerator(trainData)

if __name__ == '__main__':
    list=['煤卡车','秃头','王八','菊花']
    for i in range(20):
        print(gsw.genfromKeywords(list))


