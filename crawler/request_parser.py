import bs4
import requests
from bs4 import BeautifulSoup




def read_file(file):
    with open(file, 'r') as f:
        data = f.readline()
        return data




class TopicReviewParser:

    TOPIC_INFO_KEYS = ['data-aspect', 'data-label', 'data-positive', 'data-negative', 'data-count']
    def __init__(self):
        self.cur_topic_name = None
        self.review_container = dict()
        self.topic_infos = dict()


    def parse(self, topic_review_html, topic_info_html):
        topic_info = self.parse_topic_info(topic_info_text=topic_info_html)
        self.cur_topic_name = topic_info['data-aspect']
        self.topic_infos[self.cur_topic_name] = topic_info


        soup = BeautifulSoup(topic_review_html, 'html.parser')
        for child_soup in soup.children:
            for new_child in child_soup.children:
                self.__parse_review(new_child)


    def __parse_review(self, review_item_el: bs4.element.Tag):
        mark = self.__parse_mark(review_item_el)
        author_href = self.__parse_author(review_item_el)

        should_be_more_details = self.contains_more_details(review_item_el)

        review_text, topic_text = self.__parse_review_text(review_item_el)
        if review_text is None:
            return

        if author_href not in self.review_container:
            self.review_container[author_href] = {
                "author" : author_href,
                "text" : review_text,
                "mark" : mark,
                "should_be_more_details" : should_be_more_details,
                "topics" : {
                    self.cur_topic_name: topic_text
                }
            }
        else:
            self.review_container[author_href]['topics'][self.cur_topic_name] = topic_text



    def __parse_mark(self, review_item_el: bs4.element.Tag):
        mark_el = review_item_el.find("div", class_="KdvmLc")
        if mark_el is not None:
            return mark_el.text

        return None

    def __parse_author(self, review_item_el: bs4.element.Tag):
        author_el = review_item_el.find("a", class_="AMrStc")
        if author_el is not None:
            if "href" in author_el.attrs:
                return author_el.attrs['href']

        # author_el = review_item_el.find("a", class_="YhR3n")
        # if author_el is not None:
        #     if "href" in author_el.attrs:
        #         return author_el.attrs['href']

        return None

    def __parse_review_text(self, review_item_el: bs4.element.Tag):

        try:
            div = review_item_el.find("div", class_="K7oBsc")
            span = div.find("span")

            review_text = self.validate_if_translated(span.text)

            topic_text = None
            if span.b is not None:
                text = span.b.text
                if len(text) > 0 and text in review_text:
                    topic_text = text

            return review_text, topic_text
        except:
            return None, None

    def validate_if_translated(self, text):
        idx = len(text)
        if "(Оригінал)" in text:
            idx = text.find("(Оригінал)")

        text = text[:idx]
        text = text.replace("(Перекладено Google)", "")
        return text


    def parse_topic_info(self, topic_info_text):
        soup = BeautifulSoup(topic_info_text, 'html.parser')
        span = soup.find("span")

        topic_info = {k: v for k, v in span.attrs.items() if k in self.TOPIC_INFO_KEYS}


        return topic_info


    def generate_final_result(self):
        result = dict()
        result["topic-info"] = dict(self.topic_infos)
        result['reviews'] = list(self.review_container.values())

        return result


    def reset(self):
        self.review_container.clear()
        self.topic_infos.clear()
        self.cur_topic_name = None

    def contains_more_details(self, element:  bs4.element.Tag):
        more_detail_div = element.find("div", class_="TJUuge")
        if more_detail_div is None:
            return False

        spans = more_detail_div.findAll("span")
        for span in spans:
            if span.text == "Докладніше":
                return True
        return False





# data = read_file("test.html")
#
# topic_data = read_file("topic-test.html")
# #
# #
# parser = TopicReviewParser()
# #
# parser.parse(data, topic_data)
#
# print(parser.generate_final_result())



# soup = BeautifulSoup(data, 'html.parser')

# for child_soup in soup.children:
#     for new_child in child_soup.children:
#         print(type(new_child))
#         new_child.find("a", class_="AMrStc")
#



