import re
import numpy as np

from typing import List


class TokenNode:
    def __init__(self, token_info, head=None):
        self.token_info = token_info
        self.head = head
        self.children = []

    def get_pos(self):
        return self.token_info['upos']

    def get_deprel(self):
        return self.token_info['deprel']

    def get_head_id(self):
        return self.token_info['head']

    def get_id(self):
        return int(self.token_info['id'])

    def get_text(self):
        return self.token_info['text']

    def get_feats(self):
        return self.token_info['feats']


class NounCollocationExtractor:
    SUPPORTED_NOUN_CHILD_DEPREL = ['amod', 'advmod', 'nmod', 'conj', 'orphan']

    SUPPORTED_GRANDCHILD_DEPREL = ['advmod', 'conj', 'cc', 'punct', 'cop', 'case', 'discourse', 'nmod']

    IGNORE_NOUN_CHILD_DEPREL = ['nummod:gov']
    SUPPORTED_NOUN_HEAD_DEPREL = ['nsubj', "obj"]

    SUPPORTED_HEAD_POS = ['ADJ', 'VERB', 'ADV']

    END_STRIP_DEPREL = ['cc', 'punct', 'case', 'discourse']
    START_STRIP_DEPREL = ['cc', 'punct']
    START_STRIP_POS = ['PUNCT']

    _digits = re.compile('\d')
    a_z = re.compile('[a-z]')

    def __init__(self, nlp):
        self.nlp = nlp

    def extract_for_texts(self, texts: List[str]):
        result = []
        for text in texts:
            result += self.extract(text)

        return result

    def extract(self, text: str):
        doc = self.nlp(text)

        result = []
        for sent in doc.sentences:
            sub_sents = self.__tokenize_sent_by_coma(sent.to_dict())
            sub_sent_text = self.__build_text_from_sub_sent(sub_sents)
            sent_doc = self.nlp(sub_sent_text)
            for sub_sent in sent_doc.sentences:
                result += self.__extract_from_sent(sub_sent.to_dict())

        # result = np.unique(result).tolist()
        return self.__remove_duplicate(result)



    def __remove_duplicate(self, collocations):
        filtered_collocation = []
        ids = set()
        for collocation in collocations:
            id = self.__calc_hash_for_collocation(collocation)
            if id in ids:
                continue

            ids.add(id)
            filtered_collocation.append(collocation)

        return filtered_collocation


    #TODO: replace for normal hash
    @staticmethod
    def __calc_hash_for_collocation(collocation):
        hash_value = ""
        for token in collocation:
            hash_value += token['lemma']
        return hash_value

    def __extract_from_sent(self, sent_info):
        result = []
        noun_ids = self.__get_all_noun_ids(sent_info)
        if len(noun_ids) == 0:
            return result

        token_graph = self.__build_token_graph(sent_info)

        for noun_id in noun_ids:
            noun_token = token_graph[noun_id]
            collocation = self.__extract_collocation_for_noun(noun_token)
            if len(collocation) > 0:
                result.append(collocation)

        if self.__should_some_collocations_be_merged(result):
            result = self.__merge_collocations_if_intersect(result)

        return result

    @staticmethod
    def __tokenize_sent_by_coma(sent_info):
        result, sub_sent = [], []
        for token in sent_info:
            if 'upos' in token and token['upos'] == 'PUNCT':
                if sub_sent.count('(') != sub_sent.count(')'):
                    continue

                if 'NOUN' in [token['upos'] for token in sub_sent if 'upos' in token]:
                    result.append(sub_sent)
                    sub_sent = []
                    continue

            sub_sent.append(token)

        if len(sub_sent) > 0:
            result.append(sub_sent)

        return result

    def __extract_collocation_for_noun(self, noun_token):
        queue = self.__get_all_suitable_children(noun_token)
        if self.__is_head_suitable(noun_token):
            queue.append(noun_token.head)
        phrase_tokens = [noun_token]

        while queue:
            item = queue.pop(0)
            phrase_tokens.append(item)

            children = item.children

            for child in children:
                deprel = child.get_deprel()
                if deprel in self.IGNORE_NOUN_CHILD_DEPREL:
                    return []

                if child.get_deprel() in self.SUPPORTED_GRANDCHILD_DEPREL:
                    if self.is_suitable_token_text(child.get_text()):
                        queue.append(child)

        return self.__validate_noun_collocation(phrase_tokens)

    def __get_all_suitable_children(self, noun_token):
        queue = []

        children = noun_token.children

        for child in children:
            deprel = child.get_deprel()
            if deprel in self.SUPPORTED_NOUN_CHILD_DEPREL:
                if self.is_suitable_token_text(child.get_text()):
                    queue.append(child)

        return queue

    def __is_head_suitable(self, noun_token):
        if noun_token.head is None:
            return False

        if noun_token.token_info['deprel'] not in self.SUPPORTED_NOUN_HEAD_DEPREL:
            return False

        if noun_token.head.token_info['upos'] not in self.SUPPORTED_HEAD_POS:
            return False

        return True

    def __build_token_graph(self, sent_info):
        token_node_dict = dict()
        for token_info in sent_info:
            try:
                token_id = int(token_info['id'])
                token_node_dict[token_id] = TokenNode(token_info)
            except:
                continue

        for token_id in token_node_dict:
            token_node = token_node_dict[token_id]

            head_id = token_node.get_head_id()

            if head_id > 0:
                token_node.head = token_node_dict[head_id]
                token_node_dict[head_id].children.append(token_node)

        return token_node_dict

    def __get_all_noun_ids(self, sent_info):
        ids = []
        for token_info in sent_info:
            if 'upos' in token_info and token_info['upos'] == 'NOUN':
                ids.append(int(token_info['id']))

        return ids

    def __validate_noun_collocation(self, collocation_tokens):
        collocation_tokens.sort(key=lambda token: token.get_id())

        collocation_tokens = self.__find_max_len_non_sequence_words(collocation_tokens)

        if len(collocation_tokens) < 2:
            return []

        if not self.__is_collocation_valid_by_pos(collocation_tokens):
            return []

        collocation_tokens = self.__strip_collocation_tokens(collocation_tokens)
        if len(collocation_tokens) < 2:
            return []

        return [item.token_info for item in collocation_tokens]
        # return collocation_tokens #[item.get_text().lower() for item in collocation_tokens]

    def __merge_collocations_if_intersect(self, collocations):
        new_collocations = []
        i = 0
        while i < len(collocations) - 1:
            if int(collocations[i + 1][0]['id']) <= int(collocations[i][-1]['id']):
                merged_collocation = collocations[i]
                for j in range(0, len(collocations[i + 1])):
                    if int(collocations[i + 1][j]['id']) > int(merged_collocation[-1]['id']):
                        merged_collocation += collocations[i + 1][j:]
                        break
                new_collocations.append(merged_collocation)
                i += 1
            else:
                new_collocations.append(collocations[i])

            i += 1

        return new_collocations

    def __should_some_collocations_be_merged(self, collocations):
        for i in range(0, len(collocations) - 1):
            if int(collocations[i + 1][0]['id']) <= int(collocations[i][-1]['id']):
                return True

        return False

    def __find_max_len_non_sequence_words(self, collocation_tokens: List[TokenNode]):
        result = []
        if len(collocation_tokens) == 0:
            return result

        cur_seq = [collocation_tokens[0]]
        max_seq = cur_seq[:]
        for i in range(1, len(collocation_tokens)):
            if collocation_tokens[i].get_id() - collocation_tokens[i - 1].get_id() > 1:
                cur_seq = []
            else:
                cur_seq.append(collocation_tokens[i])

            if len(max_seq) < len(cur_seq):
                max_seq = cur_seq[:]

        return max_seq

    def __is_collocation_valid_by_pos(self, collocation_tokens: List[TokenNode]):
        noun_token, adj_token, verb_token = None, None, None
        for token in collocation_tokens:
            pos = token.get_pos()
            if pos == 'ADJ':
                adj_token = token
            elif pos == 'VERB' or pos == 'ADV':
                verb_token = token
            elif pos == 'NOUN':
                noun_token = token

        if noun_token is None:
            return False

        if verb_token is None and adj_token is None:
            return False

        if verb_token is None:
            if 'Case=Gen' in adj_token.get_feats():  # to avoid collocation like "гарячої води", but support "немає гарячої води":
                return False
        # else:
        #     if noun_token.get_id() < verb_token.get_id():  # to avoid collocation like "колеги знайшли"
        #         return False

        return True

    @staticmethod
    def __build_text_from_sub_sent(sub_sents):
        text = ""

        if len(sub_sents) == 0:
            return text

        for sub_sent in sub_sents:
            if len(sub_sent) == 0:
                continue
            text += sub_sent[0]['text'].title()
            for i in range(1, len(sub_sent)):
                text += " "
                text += sub_sent[i]["text"]
            text += ". "

        text = text.strip()

        return text

    def __strip_collocation_tokens(self, tokens: List[TokenNode]):
        result: List[TokenNode] = []

        start: bool = True
        should_add_prev_token: bool = False
        prev_token: TokenNode = None
        for token in tokens:
            if start:
                if token.get_deprel() in self.START_STRIP_DEPREL or token.get_pos() in self.START_STRIP_POS:
                    continue
                result.append(token)
                start = False
                continue

            if token.get_deprel() in self.END_STRIP_DEPREL:
                prev_token = token
                should_add_prev_token = True
                continue

            if should_add_prev_token:
                result.append(prev_token)
                should_add_prev_token = False

            result.append(token)

        return result

    def is_suitable_token_text(self, text):
        if self.contains_digits(text):
            return False

        if self.contains_ansi(text):
            return False

        return True

    def contains_digits(self, d):
        return bool(self._digits.search(d))

    def contains_ansi(self, s):
        return bool(self.a_z.match(s))

# nlp = stanza.Pipeline('uk')
#
# text_analyze = "Дуже добрий речі і приємна квартира. Затишний готель для проживання у Львові. Рекомендувати😉"
#
# extractor = NounCollocationExtractor(nlp)
#
# collocations = extractor.extract(text_analyze)
#
# print(collocations)
#
# a = 10
