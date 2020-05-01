import abc

from typing import List, Tuple

import stanfordnlp


class CollocationExtractor:

    @abc.abstractmethod
    def extract(self, text: str) -> List[str]:
        ...


class StanfordNLPCollocationExtractor(CollocationExtractor):

    MAX_WORDS_IN = 4
    COLLOCATION_TYPES = {
        "NOUN": ["VERB"],
        "PROPN": ["VERB"],
        "VERB": ["NOUN", "PROPN"],
        "ADJ": ["NOUN", 'PROPN'],
        "ADV": ["VERB"]
    }

    def __init__(self):
        self.nlp_uk = stanfordnlp.Pipeline(lang="uk")

    def extract_from_list_of_text(self, text_list: List[str]) -> List[Tuple[str, str]]:
        result = list()
        for text in text_list:
            result += self.extract(text)

        return result

    def extract(self, text: str) -> List[Tuple[str, str]]:

        collocations: List[Tuple[str, str]] = list()
        doc = self.nlp_uk(text)

        for sent in doc.sentences:
            for token in sent.dependencies:
                first = token[0].upos
                second = token[2].upos

                if self.__is_collocation(first, second):
                    collocation = self.__create_collocation(token[0].text, token[2].text, sent.tokens)
                    if len(collocation) <= self.MAX_WORDS_IN:
                        collocations.append(collocation)

        return collocations

    def __is_collocation(self, first: str, second: str):
        if first in self.COLLOCATION_TYPES:
            if second in self.COLLOCATION_TYPES:
                return True

        return False

    def __create_collocation(self, first_word, second_word, tokens):
        collocation_words = []
        any_word_found = False
        for token in tokens:
            any_word = None
            if token.text == first_word:
                any_word = first_word
            elif token.text == second_word:
                any_word = second_word

            if any_word is not None:
                collocation_words.append({
                    'word': any_word.lower(),
                    'upos': token.words[0].upos,
                    'lemma': token.words[0].lemma
                })

                if any_word_found:
                    break
                else:
                    any_word_found = True
                    continue


            if any_word_found:
                collocation_words.append({
                    'word': token.text.lower(),
                    'upos': token.words[0].upos,
                    'lemma': token.words[0].lemma
                })


        return tuple(collocation_words)


    def __filter_collocations(self, collocations):
        pass