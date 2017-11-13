import scrapy

class DataModel(scrapy.Item):
    url = scrapy.Field()
    country = scrapy.Field()
    state = scrapy.Field()
    reg_num = scrapy.Field()
    address = scrapy.Field()
    foreign_principal = scrapy.Field()
    date = scrapy.Field()
    registrant = scrapy.Field()
    exhibit_url = scrapy.Field()