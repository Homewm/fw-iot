from scrapy import Spider
from scrapy.http import Request

import FirmCrawler.items as MI
import time
import re
import urlparse

class UbloxSpider(Spider):
    name = "ublox"
    allowed_domains = ["u-blox.com"]
    start_urls = [
        #"https://www.u-blox.com/en/product-resources?field_product_tech=All&field_product_form=All&edit-submit-product-search=Go"
        "https://www.u-blox.com/en/product-resources?field_product_tech=All&field_product_form=All&edit-submit-product-search=Go&f[0]=field_file_category%3A223"
        ]


    def parse(self, response):
        item = MI.FirmcrawlerItem()
        tables = response.xpath("//div[@class='view-content']//tr")
        for t in tables:
            url = t.xpath('./td[1]/a[1]/@href').extract()[0]
            filename = url.split('/')[-1]
            version = re.search("[V,v]?\d\d?\.\d(\.\d\d?)+", filename)
            if version:
                version = version.group()
            else:
                version = ""
            item["productVersion"] = version
            item["productClass"] = "chip"  # more class
            item["productModel"] = ""
            item["description"] = ""
            item["url"] = url
            item["firmwareName"] = filename
            item["publishTime"] = ""
            item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["manufacturer"] = "u-blox"
            yield item
            print "firmware name:", item["firmwareName"]



