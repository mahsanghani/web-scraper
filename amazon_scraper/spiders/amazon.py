import re
import json
import scrapy
from urllib.parse import urljoin
from urllib.parse import urlencode
from amazon_scraper.items import AmazonScraperItem

queries = ['CBD', 'THC', 'Hemp', 'Cannabis', 'Radar', 'pills','drugs', 'knuckles', 'ammunition', 'gun', 'plants', 'fireworks',
           'meat', 'fish', 'bait', 'pets', 'alcohol', 'tobacco', 'flares', 'matches', 'furs','seeds', 'cigarettes']
# API = 'fe2936071fb6a1fa631c5584afc369e9'
# API = '015d8b29e70a01b9f516f612a9a84a3a'
# API = '4fdfb9b43af964cb9d755aa31104060d'

def get_url(url):
    payload = {'api_key': API, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):
        for query in queries:
            url = 'https://www.amazon.ca/s?' + urlencode({'k': query})
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')

        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.ca/dp/{asin}"
            yield scrapy.Request(url=get_url(product_url), callback=self.parse_product_page, meta={'asin': asin})

        next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        if next_page:
            url = urljoin("https://www.amazon.ca", next_page)
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_product_page(self, response):

        items = AmazonScraperItem()

        asin = response.meta['asin']
        name = response.xpath('//*[@id="productTitle"]/text()').extract_first()
        category = response.xpath('//a[@class="a-link-normal a-color-tertiary"]/text()').extract()
        currency = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()[0:3]
        price = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()[-5::]
        url = response.url
        description = response.xpath('//*[@id="feature-bullets"]//li/span/text()').extract()
        availability = response.xpath('//div[@id="availability"]//text()').extract()
        image = re.search('"large":"(.*?)"', response.text).groups()[0]
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        reviews = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        seller_rank = response.xpath(
            '//*[text()="Amazon Best Sellers Rank:"]/parent::*//text()[not(parent::style)]').extract()

        if not price:
            price = response.xpath('//*[@data-asin-price]/@data-asin-price').extract_first() or \
                    response.xpath('//*[@id="price_inside_buybox"]/text()').extract_first()

        items['asin'] = ''.join(asin).strip()
        items['name'] = ''.join(name).strip()
        items['category'] = ''.join(category).strip()
        items['currency'] = ''.join(currency).strip()
        items['price'] = ''.join(price).strip()
        items['url'] = ''.join(url).strip()
        items['description'] = ''.join(description).strip()
        items['availability'] = ''.join(availability).strip()
        items['image'] = ''.join(image).strip()
        items['rating'] = ''.join(rating).strip()
        items['reviews'] = ''.join(reviews).strip()
        items['seller_rank'] = ''.join(seller_rank).strip()

        yield items
