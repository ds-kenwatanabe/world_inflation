# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InflationItem(scrapy.Item):
    country = scrapy.Field()
    year = scrapy.Field()
    annual_inflation = scrapy.Field()
    average_inflation = scrapy.Field()
