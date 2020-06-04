import time
import json

from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from request_parser import TopicReviewParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def write_data_to_file(data, file):
    with open(file, "w") as f:
        f.write(data)

def write_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

def load_json(file):
    with open(file, "r") as f:
        data = json.load(f)
        return data



class GoogleReviewParser:
    def __init__(self):
        self.requst_praser = TopicReviewParser()

        chrome_options = Options()
        chrome_options.add_argument("--kiosk")

        self.driver = webdriver.Chrome(executable_path="/home/dbabenko/_Dev/Tools/chromedriver",
                                       chrome_options=chrome_options)

    def parse(self, url):
        self.open_url(url)
        self.driver.refresh()

        self.driver.execute_script("window.scrollTo(0, 500)")

        self.click_only_google()

        # self.scroll_down()

        topic_spans = self.find_all_topic_elements()

        for topic_span in topic_spans:
            self.__parse_for_topic(topic_span)

        result = self.requst_praser.generate_final_result()
        self.requst_praser.reset()
        return result

    def click_only_google(self):
        div = self.driver.find_element_by_class_name("ZDdmlb")
        div = self.find_div_by_class_name(div, "qtSVMc oU1sdf")
        div_children = div.find_elements_by_xpath("*")
        last = None
        for child in div_children:
            last = child

        if last is not None:
            try:
                last.click()
                # last.send_keys(Keys.ARROW_DOWN).perform()
                actions = ActionChains(self.driver)
                time.sleep(5)
                actions.send_keys(Keys.ARROW_DOWN).perform()
                # time.sleep(2)
                actions.send_keys(Keys.RETURN).perform()
                # time.sleep(5)

            except Exception as e:
                print("Error was here", e)

        a = 10




    def open_url(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(100)

    def __parse_for_topic(self, topic_span):

        try:

            topic_info_text = topic_span.get_attribute('innerHTML')

            # write_data_to_file(topic_span.get_attribute('innerHTML'), "topic-test.html")
            self.driver.execute_script("window.scrollTo(0, 300)")
            time.sleep(2)

            topic_span.click()
            time.sleep(1)
            self.scroll_down()

            reviews_el = self.driver.find_element_by_xpath("//div[div/@jsname='UcPrk']")

            reviews_section_els = reviews_el.find_element_by_xpath("//div[div/@jsname='Pa5DKe']")

            self.requst_praser.parse(topic_review_html=reviews_section_els.get_attribute('innerHTML'),
                                     topic_info_html=topic_info_text)

            self.scroll_up()
        except Exception as e:
            print(e)
            # raise e


        # print(0, reviews_section_els.get_attribute('innerHTML'))
        # write_data_to_file(reviews_section_els.get_attribute('innerHTML'), "test.html")
        # exit(0)
        #
        # a = 10
        # children_el = reviews_section_els.find_elements_by_xpath("*")
        # # print(1, children_el[0].get_attribute('innerHTML'))
        # #
        # print(len(children_el))
        # for child_el in children_el:
        #     new_children_el = child_el.find_elements_by_xpath("*")
        #     print(len(new_children_el))

        #
        # for child_el in children_el:
        #     print("###########################################################")
        #     print(child_el.get_attribute('innerHTML'))
        #
        #     # if self.contains_more_details(child_el):
        #     #     print("++++++++++++++++++++++++++++Here++++++++++++++++++++++++++++++++++++++")

        # print("###########################################################")

        # reviews_divs = reviews_el.find_elements_by_class_name("Svr5cf bKhjM")
        # review_div = self.driver.find_element_by_class_name("fU5h8b YYZeDd")

        a = 10

        # for review_div in review_divs:
        #     self.__parse_review(review_div)

    def find_div_by_class_name(self, element, class_name):
        divs = element.find_elements_by_tag_name("div")
        for div in divs:
            if div.get_attribute("class") == class_name:
                return div
        return None

    def contains_more_details(self, element):
        more_detail_div = self.find_div_by_class_name(element, "TJUuge")
        if more_detail_div is None:
            return False

        spans = more_detail_div.find_elements_by_tag_name("span")
        for span in spans:
            if span.text == "Докладніше":
                return True
        return False

    def click_more_details_if_needed(self, more_detail_div):
        self.driver.execute_script("window.scrollTo(0, 300)")
        # time.sleep(1000)

        divs = more_detail_div.find_elements_by_tag_name("div")
        for div in divs:
            if div.get_attribute("class") == "Jmi7d eLNT1d":
                spans = div.find_elements_by_tag_name("span")
                for span in spans:
                    if span.get_attribute("class") == "DPvwYc":
                        span.click()
                # div.click()
            # print(div.get_attribute('class'))
            # print(div.is_displayed(), div.is_selected(), div.is_enabled())
        #     if div.get_attribute("class")
        # div.click()
        # spans = more_detail_div.find_elements_by_tag_name("span")
        # for span in spans:
        #     if span.text == "Докладніше":
        #         span.click()

    def __parse_review(self, review_div):
        author_el = review_div.find_element_by_class_name("DHIhE")
        author_href = author_el.get_attribute("href")

        mark_div = review_div.find_element_by_class_name('KdvmLc')

        # mark_text = mark_div

        more_details_div = review_div.find_element_by_class_name("Jmi7d")
        more_details_div.click()

    def scroll_down(self):

        actions = ActionChains(self.driver)
        i = 0
        while i < 5:
            actions.send_keys(Keys.END).perform()
            i += 1
            time.sleep(1)
        # actions.send_keys(Keys.RETURN).perform()

        # lenOfPage = self.driver.execute_script(
        #     "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        # i = 0
        # while i < 10:
        #     match = False
        #     while (match == False):
        #         lastCount = lenOfPage
        #         time.sleep(2)
        #         lenOfPage = self.driver.execute_script(
        #             "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        #         if lastCount == lenOfPage:
        #             match = True
        #     print(lenOfPage)
        #     self.driver.execute_script("window.scrollTo(0, 1500)")
        #     time.sleep(2)
        #
        #     i += 1

    def scroll_up(self):
        self.driver.execute_script("window.scrollTo(0, 0)")

    def find_all_topic_elements(self):
        self.driver.execute_script("window.scrollTo(0, 300)")
        time.sleep(2)
        try:

            elelemts = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "xv9psc"))
            )
        except:
            return []

        # elelemts = self.driver.find_elements_by_class_name('xv9psc')

        if len(elelemts) == 0:
            return []
        el = elelemts[-1]
        spans = el.find_elements_by_tag_name('span')

        self.__click_more_span(spans)

        topic_spans = [span for span in spans if span.get_attribute('jscontroller') == "DFINgc"]

        # topic_spans[0].click()

        # print(len(topic_spans))
        #
        #
        # # spans[0]
        # self.__click_span(topic_spans[0], "G3j5r")
        # # self.__click_more_span(spans)

        return topic_spans

    def __click_span(self, span, div_class_name):
        btn = span.find_element_by_tag_name('button')
        btn.click()
        spans = btn.find_elements_by_tag_name('span')
        # for span in spans:
            # print(1)
            # print(span.text)
        #
        # print(len(spans))
        #
        # spans[3].click()

        # for div in divs:
        #     if div.get_attribute('class') == div_class_name:
        #         div.click()

    def __click_more_span(self, spans):
        for span in spans:
            jscontroller_attribute = span.get_attribute('jscontroller')
            # print(jscontroller_attribute)
            if jscontroller_attribute == 'bPWexd':
                span.click()
                # divs = span.find_elements_by_tag_name('div')
                # for div in divs:
                #     if div.get_attribute('jsname') == 'wOUyye':
                #         div.click()

    def __find_span_by_jscontroller_name(self, spans, jscontroller_name):
        for span in spans:
            if span.get_property('jscontroller') == jscontroller_name:
                return span

        return None


# with open("error.txt") as f:
#     lines = f.readlines()
#
# urls = []
# for line in lines:
#     if "Excpetion for url:" in line:
#         url = line[len("Excpetion for url:"):].strip()
#         urls.append(url)


# urls = {
#     'blum': "https://www.google.com/travel/hotels/%D0%9B%D1%8C%D0%B2%D1%96%D0%B2/entity/ChkI_aKuu6-Zl-Z7Gg0vZy8xMWY1aGxyMTM1EAE/reviews?g2lb=2502548%2C4258168%2C4260007%2C4270442%2C4274032%2C4291318%2C4305595%2C4306835%2C4317915%2C4322822%2C4328159%2C4329288%2C4356224%2C4364504%2C4366684%2C4369397%2C4373848%2C4382325%2C4385383%2C4386665%2C4386794%2C4388508%2C4270859%2C4284970%2C4291517%2C4307996%2C4356900&hl=uk&gl=ua&un=1&ap=SAE&q=%D0%B3%D0%BE%D1%82%D0%B5%D0%BB%D1%96%20%D0%BB%D1%8C%D0%B2%D0%BE%D0%B2%D0%B0&rp=EP2irruvmZfmexCKhZbrrI-1iDcQ7r6Hq9HvvqaaARCxkebHzaKKsagBOAFAAEgC&ictx=1&utm_campaign=sharing&utm_medium=link&utm_source=htls&hrf=CgUIxgoQACIDVUFIKhYKBwjkDxAGGAgSBwjkDxAGGAkYASgAsAEAWAFoAZoBDBIK0JvRjNCy0ZbQsqIBFgoIL20vMGQ3X24SCtCb0YzQstGW0LKqAQoKAgghEgIIZxgBqgEKCgIINRICCDIYAZIBAiAB"
# }


hotel_url_dict = load_json("data/hotel-kyiv-urls.json")


parser = GoogleReviewParser()

start_init = time.time()
count = 0
for url, item in hotel_url_dict.items():
# for url in urls:

    # if count < 2:
    #     count += 1
    #     continue
    # url = "https://www.google.com/travel/hotels/%D0%9A%D0%B8%D1%97%D0%B2/entity/CgsIvfST7uDzyZyvARABGmBBR1pJRWdiV1VPTEVtcHVpTWg5RTVsaFVLcG9PNTFlSm9PQVR0VFZxem41dEJ4Q1djTGhWazZWVlZmclJZYWpxdVViZDJfR2M2NmlZaV95NUpOZElFOTJZRDZqbFhVS2Y/reviews?g2lb=202153%2C2502548%2C4258168%2C4260007%2C4270442%2C4274032%2C4291318%2C4305595%2C4306835%2C4317915%2C4322822%2C4328159%2C4329288%2C4364504%2C4366684%2C4373848%2C4382325%2C4385383%2C4386665%2C4386795%2C4388508%2C4270859%2C4284970%2C4291517%2C4307996%2C4356900&hl=uk&gl=ua&un=1&rp=OAFAAEgC&ictx=1&sa=X&utm_campaign=sharing&utm_medium=link&utm_source=htls&hrf=CgUI8gwQACIDVUFIKhYKBwjkDxAGGAMSBwjkDxAGGAQYASgAsAEAWAFoAYIBJTB4NDczYWRkNzFjZWRhY2FlZDoweDdiY2M1Y2NhZjc2YjkxN2SaATESCNCa0LjRl9CyGiUweDQwZDRjZjRlZTE1YTQ1MDU6MHg3NjQ5MzFkMjE3MDE0NmZlogEVCgkvbS8wMnNuMzQSCNCa0LjRl9CyqgESCgIIIRICCAgSAggVEgIIWxgBqgEKCgIIHBICCDYYAaoBCgoCCCUSAgh6GAGqAQ4KAggREgIIQBICCAIYAaoBCgoCCC4SAgg8GAGqAQ8KAghQEgMIhAESAghPGAGqAQoKAgg1EgIIMhgBkgECIAE&ap=MABoAA&ved=2ahUKEwipv8HajeTpAhXJvxgKHSu3CIEQwIsFegUIARC6AQ"
    try:
        item = hotel_url_dict[url]
        print(url)
        hotel = item["hotel_name"]
        start = time.time()
        result = parser.parse(url)
        write_json(result, f"data/kyiv/{hotel}.json")
        print("######################################")
        print(hotel, "hotel  ", len(result['reviews']), " reviews")
        print("TMP time: ", time.time() - start)
    except Exception as e:
        print("Excpetion for url: ", url)
        print(e)
        continue
    # count += 1
    # if count == 1:
    #     break


print("Time: ", time.time() - start_init)

