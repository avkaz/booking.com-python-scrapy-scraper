# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookingScrapyScraperItem(scrapy.Item):
    url = scrapy.Field()
    breakfast = scrapy.Field()
    currency = scrapy.Field()
    price = scrapy.Field()
    occupancy = scrapy.Field()
    roomtype = scrapy.Field()
    checkin_date = scrapy.Field()
    checkout_date = scrapy.Field()
    reviews = scrapy.Field()
    rating = scrapy.Field()
    stars = scrapy.Field()
    hotelname = scrapy.Field()



