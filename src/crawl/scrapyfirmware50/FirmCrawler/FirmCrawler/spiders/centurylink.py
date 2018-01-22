from scrapy import Spider
from scrapy.http import Request

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader

import urlparse
import time

# http://home.centurytel.net/ihd/


class CenturyLinkSpider(Spider):
    name = "centurylink"
    allowed_domains = ["centurylink.com"]
    start_urls = ["http://internethelp.centurylink.com/internethelp/downloads-auto-firmware-q.html"]

    def parse(self, response):
        product = None
        for section in response.xpath("//div[@class='product-content']/div[@class='product-box2']/div"):
            text = section.xpath(".//text()").extract()
            if not section.xpath(".//a"):
                product = text[0].strip()
            else:
                for link in section.xpath(".//a/@href").extract():
                    if link.endswith(".html"):
                        yield Request(
                            url=urlparse.urljoin(response.url, link),
                            meta={"product": product,
                                  "version": FirmwareLoader.find_version(text)},
                            headers={"Referer": response.url},
                            callback=self.parse_download)

    def parse_download(self, response):
        for link in response.xpath("//div[@id='auto']//a"):
            href = link.xpath("./@href").extract()[0]
            text = link.xpath(".//text()").extract()[0]

            if ("downloads" in href or "firmware" in href) and \
                not href.endswith(".html"):
                item = FirmcrawlerItem()
                item["manufacturer"] = "centurylink"
                item["firmwareName"] = href.split('/')[-1]
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                item["url"] = href
                item["description"] = text
                item["productClass"] = ""
                item["productVersion"] = response.meta["version"]
                item["productModel"] = response.meta["product"]
                print "firmware name:",item["firmwareName"]
                yield item
                # item = FirmwareLoader(item=FirmcrawlerItem(), response=response)
                # item.add_value("version", response.meta["version"])


                # item.add_value("product", response.meta["product"])

                # yield item.load_item()
