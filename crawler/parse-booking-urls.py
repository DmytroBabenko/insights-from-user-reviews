import json
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data

def save_json_data(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)


class BookingUrlParser:
    BOOKING_PREFIX = "https://www.booking.com/hotel/ua/"

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--kiosk")

        self.driver = webdriver.Chrome(executable_path="/home/dbabenko/Downloads/chromedriver_linux64/chromedriver",
                                       chrome_options=chrome_options)

        self.hotel_url_dict = dict()

    def parse(self, urls_dict):

        google_booking_association = dict()
        # i = 0
        for url, item in urls_dict.items():
            try:
                booking_id = self.parse_url(url)
                if booking_id is None:
                    continue

                hotel_name = item['hotel_name']
                google_booking_association[hotel_name] = booking_id

                # i += 1
                #
                # if i >= 5:
                #     break

            except Exception as e:
                print(url)
                print(e)

        return google_booking_association

    def parse_url(self, url: str):
        self.open_url(url)

        body = self.driver.find_element_by_id('yDmH0d')
        text = body.get_attribute('innerHTML')
        booking_id = self.__parse_booking(text)

        return booking_id

    def open_url(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(100)

    def __parse_booking(self, text_body):
        booking_idx = text_body.find(self.BOOKING_PREFIX)
        if booking_idx == -1:
            return None

        start_idx = booking_idx + len(self.BOOKING_PREFIX)

        booking_end_idx = text_body[start_idx:].find('?')
        if booking_end_idx == -1:
            return None

        return text_body[start_idx: start_idx + booking_end_idx]

lviv_urls_dict = load_json('hotel-lviv-urls.json')
kyiv_urls_dict = load_json('hotel-kyiv-urls.json')

urls_dict = {**lviv_urls_dict, **kyiv_urls_dict}

parser = BookingUrlParser()
google_booking_association = parser.parse(urls_dict)

save_json_data(google_booking_association, 'google-booking-association.json')

a = 10
