# coding:utf-8

import sys
#sys.path.append("./model")

import tensorflow as tf
import numpy as np

from gushiwenModel.utils import *
from gushiwenModel.data import *
sys.path.append("../modern2poem/association")
import association

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

        self.associator=association.Associator()

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

    def probsToWord(self, weights, words):
        prefixSum = np.cumsum(weights) #按概率随机抽取
        ratio = np.random.rand(1)
        index = np.searchsorted(prefixSum, ratio * prefixSum[-1]) # large margin has high possibility to be sampled
        return words[index[0]]

    def genfromKeywords(self,keywords):
        """
        从sxhy古词生成古诗
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
                x = np.array([[self.trainData.wordToID[thisword]]])
                probs2, state = self.sess.run([self.probs, self.finalState], feed_dict={self.gtX: x, self.initState: state})
                if wordlasting >= 2:wordlasting -= 1
                else:
                    word = self.probsToWord(probs2, self.trainData.words)
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

    def genfromSentence(self,sentence):
        """

        :param sentence: 一个汉语句子即可
        :return:
        """
        keywords=self.associator.assoRandom(sentence,assoLen=8)
        return self.genfromKeywords(keywords)

if __name__ == '__main__':
    trainData = POEMS(trainPoems)
    gsw=GushiwenGenerator(trainData)
    list=['四时','炊烟','袅袅','升腾']
    print(gsw.genfromKeywords(list))


