import abc

from typing import List, Tuple

import stanfordnlp


class CollocationExtractor:

    @abc.abstractmethod
    def extract(self, text: str) -> List[str]:
        ...


class StanfordNLPCollocationExtractor(CollocationExtractor):
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
                    collocations.append((token[0].text.lower(), token[2].text.lower()))

        return collocations

    def __is_collocation(self, first: str, second: str):
        if first in self.COLLOCATION_TYPES:
            if second in self.COLLOCATION_TYPES:
                return True

        return False

# sentence_example = "Чоловік був щирий та добре поводився зі своїм котом."


# collocation_extractor = StanfordNLPCollocationExtractor()
#
# collocations = collocation_extractor.extract(sentence_example)
#
# for collocation in collocations:
#     print(collocation)


# nlp= stanfordnlp.Pipeline(lang="uk")
# doc = nlp(sentence_example)
#
# for sent in doc.sentences:
#     for token in sent.dependencies:
#         print(token)
#         print("#############################")
