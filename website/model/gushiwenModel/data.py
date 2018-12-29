# coding: UTF-8
from gushiwenModel.utils import *
from paths import raw_dir
import os

_pinyin_path = pinyinPath


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

