from typing import Dict
from gensim.models.keyedvectors import Word2VecKeyedVectors
from fuzzyset import FuzzySet

class WordFixer:

    def __init__(self, word2vec: Word2VecKeyedVectors):
        self.__word2vec = word2vec
        self.__fixed_word_dict: Dict[str, str] = dict()

        self.__approximate_matcher = FuzzySet(word2vec.vocab)



    def is_word_correct(self, word: str):
        if word in self.__word2vec:
            return True
        return False



    def fix(self, word: str):

        if word in self.__fixed_word_dict:
            return self.__fixed_word_dict[word]

        candidate = self.__approximate_matcher.get(word)
        if candidate is not None and len(candidate) > 0:
            fixed_word = candidate[0][1]
            self.__fixed_word_dict[word] = fixed_word
            return fixed_word

        raise Exception("Cannot be fixed")
        