import abc

from topics import TopicType, POTENTIAL_TOPIC_LEMMAS


class TopicDetector:

    @abc.abstractmethod
    def detect_cluster_topic_type(self, cluster):
        ...


class RuleBasedTopicDetector(TopicDetector):
    def detect_cluster_topic_type(self, cluster):
        pos_counter = {
            'NOUN': dict(),
            'ADV': dict(),
            'ADJ': dict()
        }

        for item in cluster:
            for word_item in item:
                lemma = word_item['lemma']
                pos = word_item['upos']
                if pos in pos_counter:
                    if lemma not in pos_counter[pos]:
                        pos_counter[pos][lemma] = 1
                    else:
                        pos_counter[pos][lemma] += 1

        for pos in pos_counter:
            pos_counter[pos] = {k: v for k, v in
                                sorted(pos_counter[pos].items(), key=lambda item: item[1], reverse=True)}

        for pos in pos_counter:
            for lemma in pos_counter[pos]:
                for topic_type in POTENTIAL_TOPIC_LEMMAS:
                    if lemma in POTENTIAL_TOPIC_LEMMAS[topic_type]:
                        return topic_type

        return TopicType.OTHERS
