# coding:utf-8

import sys
#sys.path.append("./model")

import tensorflow as tf
import numpy as np

from gushiwenModel.gswutils import *
from gushiwenModel.data import *

#sys.path.append("../modern2poem/association")
#import association

class GushiwenGenerator(object):
    def __init__(self, trainData):
        self.trainData = trainData
        self.gtX = tf.placeholder(tf.int32, shape=[1, None])  # input
        self.logits, self.probs, self.stackCell, self.initState, self.finalState = self.buildModel(self.trainData.wordNum, self.gtX)
        self.sess=tf.Session()

        self.sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
        saver.restore(self.sess, checkPoint.model_checkpoint_path)
        print("restored %s" % checkPoint.model_checkpoint_path)

        #self.associator=association.Associator()

    def buildModel(self, wordNum, gtX, hidden_units = 128, layers = 2):
        with tf.variable_scope("embedding"): #embedding
            embedding = tf.get_variable("embedding", [wordNum, hidden_units], dtype = tf.float32)
            inputbatch = tf.nn.embedding_lookup(embedding, gtX)

        basicCell = tf.contrib.rnn.BasicLSTMCell(hidden_units, state_is_tuple = True)
        stackCell = tf.contrib.rnn.MultiRNNCell([basicCell] * layers)
        initState = stackCell.zero_state(np.shape(gtX)[0], tf.float32)
        outputs, finalState = tf.nn.dynamic_rnn(stackCell, inputbatch, initial_state = initState)
        outputs = tf.reshape(outputs, [-1, hidden_units])

        with tf.variable_scope("softmax"):
            w = tf.get_variable("w", [hidden_units, wordNum])
            b = tf.get_variable("b", [wordNum])
            logits = tf.matmul(outputs, w) + b

        probs = tf.nn.softmax(logits)
        return logits, probs, stackCell, initState, finalState

    def probsToWord(self,weights,poemnow,prondict,words):
        num_per_sen=poemnow.find('，')
        used_chars = set(ch for ch in poemnow)
        idx=len(poemnow)
        for i in range(len(weights[0])):
            ch=words[i]
            if ch in used_chars:
                weights[0][i]*=0.6#防止过多叠词，目前还学不到凄凄惨惨戚戚的程度

            if num_per_sen>1:#第一句已经做出来了
                if ((idx-num_per_sen+1)/(num_per_sen+1))%2==1 and \
                    not prondict.co_rhyme(ch,poemnow[num_per_sen-1]):
                    weights[0][i]*=0.001#一三五不论，二四六分明

                counterind=idx%(num_per_sen+1)
                if 1==counterind and \
                    not prondict.counter_tone(poemnow[1],ch):
                    weights[0][i]*=0.4#平仄
                if counterind>1 and counterind%2==1 and \
                    not prondict.counter_tone(poemnow[idx-1],ch):
                    weights[0][i]*=0.4

        prefixSum = np.cumsum(weights) #按概率随机抽取
        ratio = np.random.rand(1)
        index = np.searchsorted(prefixSum, ratio * prefixSum[-1]) # large margin has high possibility to be sampled
        return words[index[0]]

    def genfromKeywords(self,keywords):
        """
        从sxhy古词生成古诗，keywords长度至少为4（通过前面拓展）
        :param keywords:list，其中词应该全部来源于sxhy,通过在上一步设置用户选择框得到
        :return:
        """
        state = self.sess.run(self.stackCell.zero_state(1, tf.float32))
        x = np.array([[self.trainData.wordToID['[']]])
        probs1, state = self.sess.run([self.probs, self.finalState], feed_dict={self.gtX: x, self.initState: state})

        flag = 1
        endSign = {-1: "，", 1: "。"}
        poem = ''

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
                poem += '\n'
            else:
                probs2, state = self.sess.run([self.probs, self.finalState],
                                         feed_dict={self.gtX: np.array([[self.trainData.wordToID["，"]]]), self.initState: state})

        return poem

    '''
    def genfromSentence(self,sentence):这里在13行import association时会出现文件路径问题，需最后调整（绝对）路径
        """

        :param sentence: 一个汉语句子即可
        :return:
        """
        keywords=self.associator.assoRandom(sentence,assoLen=8)
        return self.genfromKeywords(keywords)
        
    '''

if __name__ == '__main__':
    trainData = POEMS(trainPoems)
    gsw=GushiwenGenerator(trainData)
    list=['煤卡车','秃头','王八','菊花']
    for i in range(20):
        print(gsw.genfromKeywords(list))


