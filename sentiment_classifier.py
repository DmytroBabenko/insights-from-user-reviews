import numpy as np

from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

from utils import Utils


class SentimentClassifier:
    MAX_LENGTH = 5
    trunc_type = 'post'
    padding_type = 'post'

    LABEL_TO_IDX = {
        'pos': 0,
        'neg': 1,
        'neg': 2
    }

    LABELS = ['pos', 'neg', 'neg']

    def __init__(self, model_file, word_index_file):
        self.model = keras.models.load_model(model_file)
        self.word_index = Utils.load_json(word_index_file)

    def predict_sentiments_for_collocations(self, collocations):
        sequences = [self.collocation2sequence(collocation) for collocation in collocations]
        padded = self.padding(sequences)
        pred = self.model.predict(padded)
        # print(np.max(pred, -1))
        return [self.LABELS[idx] for idx in np.argmax(pred, -1)]

    def predict_sentiment_for_cluster(self, collocations=None, sentiments=None):
        if collocations is None and sentiments is None:
            raise Exception("Invalid argument. At least parameter should be specified")

        if sentiments is None:
            sentiments = self.predict_sentiments_for_collocations(collocations)

        pos_count, neut_count, neg_count = 0, 0, 0
        for sentiment in sentiments:
            if sentiment == 'pos':
                pos_count += 1
            elif sentiment == 'neg':
                neg_count += 1
            else:
                neut_count += 1

        if pos_count > neg_count and pos_count > neut_count:
            return 'pos'

        if neg_count > pos_count and neg_count > neut_count:
            return 'neg'

        return 'neg'



    def padding(self, sequences):
        padded = pad_sequences(sequences,
                               maxlen=self.MAX_LENGTH,
                               padding=self.padding_type,
                               truncating=self.trunc_type)

        return padded

    def collocation2sequence(self, collocation):
        seq = []
        for token in collocation:
            word = token['lemma']
            if word in self.word_index:
                seq.append(self.word_index[word])
        #         else:
        #             seq.append(word_idx[oov_tok])
        return seq


# collocation_examples = [[{'id': '1',
#    'text': 'У',
#    'lemma': 'у',
#    'upos': 'ADP',
#    'xpos': 'Spsl',
#    'feats': 'Case=Loc',
#    'head': 2,
#    'deprel': 'case',
#    'misc': 'start_char=0|end_char=1'},
#   {'id': '2',
#    'text': 'готелі',
#    'lemma': 'готель',
#    'upos': 'NOUN',
#    'xpos': 'Ncmsln',
#    'feats': 'Animacy=Inan|Case=Loc|Gender=Masc|Number=Sing',
#    'head': 4,
#    'deprel': 'orphan',
#    'misc': 'start_char=2|end_char=8'},
#   {'id': '3',
#    'text': 'погане',
#    'lemma': 'поганий',
#    'upos': 'ADJ',
#    'xpos': 'Afpnsns',
#    'feats': 'Case=Nom|Degree=Pos|Gender=Neut|Number=Sing',
#    'head': 4,
#    'deprel': 'amod',
#    'misc': 'start_char=9|end_char=15'},
#   {'id': '4',
#    'text': 'кондиціонування',
#    'lemma': 'кондиціонування',
#    'upos': 'NOUN',
#    'xpos': 'Ncnsnn',
#    'feats': 'Animacy=Inan|Case=Nom|Gender=Neut|Number=Sing',
#    'head': 0,
#    'deprel': 'root',
#    'misc': 'start_char=16|end_char=31'}]]
#
#
#
# collocation_sent_classifier = SentimentClassifier('models/sentiment-collocation.json',
#                                                   'models/sent-collocation-word-index.json')
#
# r = collocation_sent_classifier.predict_sentiment_for_cluster(collocation_examples)
#
# print(r)
#
# a = 10