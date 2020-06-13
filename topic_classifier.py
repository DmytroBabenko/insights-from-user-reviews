import pickle
import numpy as np

from utils import Utils


def get_nouns_in_collocation(collocation):
    tokens = []
    #     print(1, collocation)
    for token in collocation:
        #         print(2, token)
        if token['upos'] == 'NOUN':
            tokens.append(token)
    return tokens




class TopicClassifier:

    def __init__(self, model_file, fast_text_model):
        self.model = pickle.load(open(model_file, 'rb'))
        self.ft = fast_text_model

    def predict(self, collocations):
        X, filtered_collocations = self.__convert_data_to_X(collocations)
        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X)

        return self.convert_pred_to_suitable_result(y_pred, y_proba, filtered_collocations)

    def __convert_data_to_X(self, data):
        new_data, X = [], []
        for item in data:
            noun_tokens = get_nouns_in_collocation(item)
            if len(noun_tokens) == 0:
                continue

            v = np.array(300 * [0.0])
            for noun_token in noun_tokens:
                v += self.ft.get_word_vector(noun_token['lemma'])

            v /= len(noun_tokens)

            X.append(v)
            new_data.append(item)

        return np.array(X), new_data

    @staticmethod
    def convert_pred_to_suitable_result(y, y_proba, hotel_collocations):
        visible_result, pos_result = dict(), dict()
        size = len(hotel_collocations)
        for i in range(size):
            if y[i] not in visible_result:
                visible_result[y[i]] = []
            if y[i] not in pos_result:
                pos_result[y[i]] = []

            collocation_text = Utils.generate_text_from_collocation(hotel_collocations[i])
            visible_result[y[i]].append((collocation_text, max(y_proba[i])))
            pos_result[y[i]].append((hotel_collocations[i], max(y_proba[i])))

        return visible_result, pos_result

    # @staticmethod
    # def select_n_for_each_topic(topic_collocations, n, sent):
    #     result = dict()
    #
    #     for topic in topic_collocations:
    #         collocations = [item for item in topic_collocations[topic] if item[1] == sent]
    #         collocations = sorted(collocations, key=lambda item: (item[1], len(item[0])), reverse=True)
    #
    #         n = min(n, len(collocations))
    #         selected_collocations = [item[0] for item in collocations[:n]]
    #         result[topic] = selected_collocations
    #
    #     return result


    @staticmethod
    def select_n_collocation_by_sentiment(topic_collocations, n, sent):

        collocations = [item for item in topic_collocations if item[2] == sent]
        collocations = sorted(collocations, key=lambda item: (item[1], len(item[0])), reverse=True)

        n = min(n, len(collocations))
        selected_collocations = [item[0] for item in collocations[:n]]

        return selected_collocations

