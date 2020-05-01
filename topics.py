from enum import IntEnum
import abc


from enum import Enum


class TopicType(Enum):
    CLEAN = "clean",
    COMFORT = "comfort",
    LOCATION = "location",
    SERVICES = "services",
    STAFF = "staff",
    VALUE = "value",
    WIFI = "wi-fi",
    OTHERS = "others"


POTENTIAL_TOPIC_LEMMAS = {
    TopicType.CLEAN : {'чисто', "брудно", "чистота", "бруд", "сміття"},
    TopicType.COMFORT : {'зручний', 'затишний', 'атмосфера', 'тихий', "шумний"},
    TopicType.LOCATION : {'локація', 'розташування', 'місце', 'центр', "далеко", "близько"},
    TopicType.SERVICES : {"сервіс"},
    TopicType.STAFF : {'персонал', 'рецепція'},
    TopicType.VALUE : {"дорогий", "дешевий", "співвідношення", "ціна", "якість"},
    TopicType.WIFI : {"інтернет", 'wi-fi', "сигнал"},
}