from scrapy import Spider

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader
import time
import urlparse
# need 2 minutes to load page
class SeikiSpider(Spider):
    name = "seiki"
    allowed_domains = ["seiki.com"]
    start_urls = ["http://www.seiki.com/support/download"]

    def parse(self, response):
        for entry in response.xpath(
                "//div[@class='main-container']//p|//div[@class='main-container']//ul"):
            text = entry.xpath(".//text()").extract()

            for href in entry.xpath(".//a/@href").extract():
                if "Firmware" in href:
                    item = FirmcrawlerItem()
                    item["productVersion"] = ""
                    item["publishTime"] = ""
                    item["productClass"] = ""
                    item["productModel"] = FirmwareLoader.find_product(text)
                    item["description"] = ""
                    item["url"] = urlparse.urljoin(response.url,href)
                    item["firmwareName"] = href.split('/')[-1]
                    item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    item["manufacturer"] = "seiki"
                    yield item
                    print "firmware name:", item["firmwareName"]


