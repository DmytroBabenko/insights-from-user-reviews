import json
import numpy as np
import glob

from sklearn.metrics import classification_report, f1_score

inv_merged_topic = dict({
    'Fitness': ['Spa', 'Gym', 'Pool', 'Wellness'],
    'Room amenities': ['Room entertainment', 'Safety'],
    'Property': ['Accessibility'],
    'Food and Beverage': ['Restaurant'],
    'Other': ['Air conditioning', 'Hot tub', 'Pets', 'Bar or lounge', 'Beach']})


class Utils:

    @staticmethod
    def generate_text_from_collocation(collocation):
        text = collocation[0]['text'].lower()

        for i in range(1, len(collocation)):
            token = collocation[i]
            if 'upos' in token and token['upos'] != 'PUNCT':
                text += " "
            text += token['text'].lower()

        return text

    @staticmethod
    def load_json(file):
        with open(file, 'r') as f:
            data = json.load(f)
        return data

    @staticmethod
    def get_google_hotel_review_file(directory, hotel_name):
        kyiv_files = glob.glob(f"{directory}/kyiv/*.json")
        lviv_files = glob.glob(f"{directory}/lviv/*.json")

        for file in kyiv_files + lviv_files:
            cur_hotel_name = file.split('/')[-1].replace('.json', '').strip().lower()

            if hotel_name.strip().lower() == cur_hotel_name:
                return file

        return None

    @staticmethod
    def calc_true_sentiment_for_google_hotel(topics_info, topic_name):
        if topic_name not in topics_info:
            return 'neg'

        topics = [topic_name]
        if topic_name in inv_merged_topic:
            topics += inv_merged_topic[topic_name]

        pos_count, neut_count, neg_count = [], [], []

        for topic in topics:
            if topic not in topics_info:
                continue
            topic_info = topics_info[topic]
            pos_count_i = int(topic_info['data-positive']) if 'data-positive' in topic_info else 0
            neg_count_i = int(topic_info['data-negative']) if 'data-positive' in topic_info else 0

            data_count = int(topic_info['data-count'])
            neut_count_i = data_count - (pos_count_i + neg_count_i)

            pos_count.append(pos_count_i)
            neut_count.append(neut_count_i)
            neg_count.append(neg_count_i)

        pos_count = np.average(pos_count) if len(pos_count) != 0 else 0
        neut_count = np.average(neut_count) if len(neut_count) != 0 else 0
        neg_count = np.average(neg_count)  if len(neg_count) != 0 else 0

        if pos_count > neg_count and pos_count > neut_count:
            return 'pos'

        if neg_count > pos_count and neg_count > neut_count:
            return 'neg'

        return 'neg'

        # neut_count = int(topic_info['data-negative']) if 'data-positive' in topic_info else 0

    @staticmethod
    def     calc_classification_report_for_each_topic(hotels, hotel_reviews,
                                                  collocation_extractor,
                                                  topic_classifier,
                                                  collocation_sent_classifier):
        topic_sent_reports = dict()
        for google_hotel in hotels:
            if google_hotel not in hotel_reviews:
                continue

            hotel_collocations = collocation_extractor.extract_for_texts(hotel_reviews[google_hotel]['texts'])

            if len(hotel_collocations) == 0:
                continue

            _, topic_collocations = topic_classifier.predict(hotel_collocations)

            for topic in topic_collocations:
                collocations = [item[0] for item in topic_collocations[topic]]
                pred_sent = collocation_sent_classifier.predict_sentiment_for_cluster(collocations=collocations)
                true_sent = Utils.calc_true_sentiment_for_google_hotel(hotel_reviews[google_hotel]['topic-info'],
                                                                       topic)

                if topic not in topic_sent_reports:
                    topic_sent_reports[topic] = {
                        'true': [true_sent],
                        'pred': [pred_sent]
                    }
                else:
                    topic_sent_reports[topic]['true'].append(true_sent)
                    topic_sent_reports[topic]['pred'].append(pred_sent)

        for topic in topic_sent_reports:
            f1 = f1_score(topic_sent_reports[topic]['true'], topic_sent_reports[topic]['pred'], average='micro')

            topic_sent_reports[topic] = (classification_report(topic_sent_reports[topic]['true'],
                                                              topic_sent_reports[topic]['pred']), f1)

        return topic_sent_reports


    @staticmethod
    def get_booking_review_texts(booking_df, hotel):
        hotel_df = booking_df.loc[booking_df['hotel'] == hotel]
        if len(hotel_df) == 0:
            return []

        texts = []
        for i in range(len(hotel_df)):
            title = hotel_df['title'].values[i]
            pos = hotel_df['pos_text'].values[i]
            neg = hotel_df['neg_text'].values[i]

            text = ""
            if len(title) > 0 and title != 'Nan':
                text += title
                text += ". "

            if len(pos) > 0 and pos != 'Nan':
                text += pos
                text += ". "

            if len(neg) > 0 and neg != 'Nan':
                text += neg

            texts.append(text.strip())

        return texts

    @staticmethod
    def define_sentiments_and_summary(topic_collocations,
                                      visible_topic_collocations,
                                      collocation_sent_classifier,
                                      topic_classifier, n=1):

        topic_collocations_sent = dict()
        topic_summary = dict()
        for topic in topic_collocations:
            collocations = [item[0] for item in topic_collocations[topic]]
            sentiments = collocation_sent_classifier.predict_sentiments_for_collocations(collocations)

            topic_collocations_sent[topic] = [(visible_topic_collocations[topic][i][0],
                                               visible_topic_collocations[topic][i][1],
                                               sentiments[i])
                                              for i in range(len(sentiments))]

            topic_sentiment = collocation_sent_classifier.predict_sentiment_for_cluster(sentiments=sentiments)
            pos_sents = sentiments.count('pos')
            neg_sents = sentiments.count('neg')

            sent_collocations = topic_classifier.select_n_collocation_by_sentiment(topic_collocations_sent[topic], n,
                                                                                   topic_sentiment)

            topic_summary[topic] = {
                'sentiment': topic_sentiment,
                'phrases': sent_collocations,
                'pos_count': pos_sents,
                'neg_count' : neg_sents,
            }

        return topic_collocations_sent, topic_summary

    @staticmethod
    def print_hotel_summary(topic_summary_dict, detailed=True):
        for topic in topic_summary_dict:
            if detailed:
                print("\n#######################################")
                pos_count = topic_summary_dict[topic]["pos_count"]
                neg_count = topic_summary_dict[topic]["neg_count"]
                print("TOPIC: ", topic, f"( mention in {pos_count} positively and in {neg_count} negatively )")

            sentiment = topic_summary_dict[topic]['sentiment']
            prefix = ""
            if sentiment == 'pos':
                prefix = "+"
            elif sentiment == 'neg':
                prefix = "-"

            if detailed:
                print("SENTIMENT: ", sentiment)

            for phrase in topic_summary_dict[topic]['phrases']:
                print(f"\t{prefix} {phrase}")

# directory = "dataset/google"
# Utils.get_google_hotel_review_file(directory, 'Art Deco Central Rooms')
