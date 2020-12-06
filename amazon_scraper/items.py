import scrapy


class AmazonScraperItem(scrapy.Item):
    asin = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    currency = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    availability = scrapy.Field()
    image = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()
    seller_rank = scrapy.Field()