import json
import time

from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import bs4
import requests
from bs4 import BeautifulSoup

def write_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

class HotelReviewUrlParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--kiosk")

        self.driver = webdriver.Chrome(executable_path="/home/dbabenko/_Dev/Tools/chromedriver",
                                       chrome_options=chrome_options)


        self.hotel_url_dict = dict()





    def parse(self, start_url):
        self.open_url(start_url)

        page = 1
        ret = True
        while ret:
            div = self.driver.find_element_by_class_name("l5cSPd")
            self.parse_hotel_url_dict(div.get_attribute('innerHTML'))

            self.scroll_down()
            ret = self.click_next()
            self.driver.refresh()
            print("Page: ", page)
            page += 1




    def open_url(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(100)


    def parse_hotel_url_dict(self, html_text ):
        soup = BeautifulSoup(html_text, 'html.parser')
        hotel_elements = soup.findAll("c-wiz", class_="f1dFQe")

        for hotel_element in hotel_elements:
            try:
                a_el = hotel_element.find("a", "PVOOXe")
                hotel_name = a_el.attrs['aria-label']

                a_ref_el = hotel_element.find("a", class_="spNMC lRagtb")
                ref = a_ref_el.attrs['href']
                href = f"https://www.google.com/{ref}"

                item = {
                    'hotel_name': hotel_name,
                    'url': href
                }

                self.hotel_url_dict[href] = item
            except:
                continue

    def scroll_down(self):

        actions = ActionChains(self.driver)
        i = 0
        while i < 1:
            actions.send_keys(Keys.END).perform()
            i += 1


    def generate_result(self):
        return self.hotel_url_dict

    def reset(self):
        self.hotel_url_dict.clear()


    def click_next(self):
        div = self.driver.find_element_by_class_name("J6e2Vc")
        next_btn = self.find_div_by_class_name(div, "U26fgb O0WRkf oG5Srb C0oVfc JDnCLc yHhO4c yNl8hd zbLWdb")
        if next_btn is None:
            return False
        next_btn.click()
        return True




    def find_div_by_class_name(self, element, class_name):
        divs = element.find_elements_by_tag_name("div")
        for div in divs:
            if div.get_attribute("class") == class_name:
                return div
        return None



url_parser = HotelReviewUrlParser()

# url_parser.parse("https://www.google.com/travel/hotels/%D0%9B%D1%8C%D0%B2%D1%96%D0%B2?g2lb=2502548%2C4258168%2C4260007%2C4270442%2C4274032%2C4291318%2C4305595%2C4306835%2C4317915%2C4322822%2C4328159%2C4329288%2C4364504%2C4366684%2C4373848%2C4382325%2C4385383%2C4386665%2C4386794%2C4388508%2C4270859%2C4284970%2C4291517%2C4307996%2C4356900&hl=uk&gl=ua&un=1&rp=EP2irruvmZfmexD9oq67r5mX5ns4AUAASAI&ictx=1&sa=X&utm_campaign=sharing&utm_medium=link&utm_source=htls&hrf=CgUIxgoQACIDVUFIKhYKBwjkDxAGGAgSBwjkDxAGGAkYASgAsAEAWAFoAYIBJTB4NDczYWRkNzFjZWRhY2FlZDoweDdiY2M1Y2NhZjc2YjkxN2SaATMSCtCb0YzQstGW0LIaJTB4NDczYWRkN2MwOTEwOWE1NzoweDQyMjNjNTE3MDEyMzc4ZTKiARYKCC9tLzBkN19uEgrQm9GM0LLRltCyqgEKCgIIIRICCGcYAaoBCgoCCDUSAggyGAGSAQIgAQ&ap=EgNDQXcwAw")

url_parser.parse("https://www.google.com/travel/hotels/%D0%9A%D0%B8%D1%97%D0%B2?g2lb=202153%2C2502548%2C4258168%2C4260007%2C4270442%2C4274032%2C4291318%2C4305595%2C4306835%2C4317915%2C4322822%2C4328159%2C4329288%2C4364504%2C4366684%2C4373848%2C4382325%2C4385383%2C4386665%2C4386795%2C4388508%2C4270859%2C4284970%2C4291517%2C4307996%2C4356900&hl=uk&gl=ua&un=1&rp=OAFAAEgC&ictx=1&sa=X&utm_campaign=sharing&utm_medium=link&utm_source=htls&hrf=CgUI8gwQACIDVUFIKhYKBwjkDxAGGAMSBwjkDxAGGAQYASgAsAEAWAFoAYIBJTB4NDczYWRkNzFjZWRhY2FlZDoweDdiY2M1Y2NhZjc2YjkxN2SaATESCNCa0LjRl9CyGiUweDQwZDRjZjRlZTE1YTQ1MDU6MHg3NjQ5MzFkMjE3MDE0NmZlogEVCgkvbS8wMnNuMzQSCNCa0LjRl9CyqgESCgIIIRICCAgSAggVEgIIWxgBqgEKCgIIHBICCDYYAaoBCgoCCCUSAgh6GAGqAQ4KAggREgIIQBICCAIYAaoBCgoCCC4SAgg8GAGqAQ8KAghQEgMIhAESAghPGAGqAQoKAgg1EgIIMhgBkgECIAE&ap=MABoAA")

result = url_parser.generate_result()
write_json(result, "data/hotel-kyiv-urls.json")



a = 10






