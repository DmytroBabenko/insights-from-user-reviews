import nltk
import numpy as np
from nltk.cluster import KMeansClusterer
from gensim.models import KeyedVectors


class ClusterCollocations:
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.embed_size = len(self.word2vec['1'])


    def cluster_collocations(self, collocations, num_cluster):
        X, filtered_collocations = self.__convert_collocations_to_embedding_vectors(collocations)
        kclusterer = KMeansClusterer(num_cluster, distance=nltk.cluster.util.cosine_distance, avoid_empty_clusters=True, repeats=100)
        y = kclusterer.cluster(X, assign_clusters=True)

        top_indices = self.__find_top_n_gram_indices(X, y, kclusterer.means())

        result = dict()
        for i in range(0, len(y)):
            if y[i] not in result:
                result[y[i]] = {
                    'collocations' : [filtered_collocations[i]],
                    'centroid': filtered_collocations[top_indices[y[i]]]
                }
            else:
                result[y[i]]['collocations'].append(filtered_collocations[i])

        return result

    def __find_top_n_gram_indices(self, X, y, centroids):
        min_dis = len(centroids) * [100]
        top_indices = len(centroids) * [-1]
        for i in range(0, len(centroids)):
            for j in range(0, len(X)):
                if y[j] != i:
                    continue

                dis = nltk.cluster.util.cosine_distance(X[j], centroids[i])
                if min_dis[i] > dis:
                    min_dis[i] = dis
                    top_indices[i] = j

        return top_indices

    def __convert_collocations_to_embedding_vectors(self, collocations):
        max_length = self.__calc_max_potential_len_of_collocations(collocations)
        X = []
        filtered_collocations = []
        for collocation in collocations:
            if len(collocation) < 2:
                continue

            x = self.__convert_collocation_to_vector(collocation, max_length)
            if x is None:
                continue

            filtered_collocations.append(collocation)
            X.append(x)

        return np.array(X), filtered_collocations

    @staticmethod
    def __calc_max_potential_len_of_collocations(collocations):
        max_size = 0
        for collocation in collocations:
            if max_size < len(collocation):
                max_size = len(collocation)

        return max_size

    def __convert_collocation_to_vector(self, collocation, max_length):
        word = self.__get_word_for_build_vector(collocation)
        if word is None:
            return None
        x = self.word2vec[word].tolist()
        return x

    def __get_word_for_build_vector(self, collocation):

        noun_lemma, verb_lemma = None, None
        for item in collocation:
            if item["upos"] == 'NOUN':
                noun_lemma = item['lemma']

            if item["upos"] == 'VERB':
                verb_lemma = item['lemma']

        if noun_lemma is not None:
            if noun_lemma in self.word2vec:
                return noun_lemma

        if verb_lemma is not None:
            if verb_lemma in self.word2vec:
                return verb_lemma

        return None
