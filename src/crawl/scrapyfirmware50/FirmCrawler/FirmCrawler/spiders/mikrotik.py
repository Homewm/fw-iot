from scrapy import Spider
from scrapy.http import FormRequest

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader

import urlparse
import time


class MikrotikSpider(Spider):
    name = "mikrotik"
    allowed_domains = ["mikrotik.com"]
    start_urls = ["http://www.mikrotik.com/download"]

    def parse(self, response):
        for arch in ["1", "2", "3", "4", "5", "6", "swos"]:
            for pub in ["1", "2", "3", "4", "5"]:
                yield FormRequest(
                    url=urlparse.urljoin(response.url, "/client/ajax.php"),
                    formdata={"action": "getRouterosArch",
                              "arch": arch, "pub": pub},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_product)

    def parse_product(self, response):
        for href in response.xpath("//a/@href").extract():
            if href.endswith(".npk") or href.endswith(".lzb"):
                text = response.xpath("//text()").extract()
                basename = href.split("/")[-1]
                item = FirmcrawlerItem()
                item["productVersion"] = FirmwareLoader.find_version_period(text)
                item["productModel"] = basename[0: basename.rfind("-")]
                item["description"] = ""
                item["productClass"] = ""  # more class
                item["url"] = href
                item["firmwareName"] = item["url"].split('/')[-1]
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                item["manufacturer"] = "mikrotik"
                item["publishTime"] = FirmwareLoader(date_fmt=["%Y-%m-%d"]).find_date(text)
                yield item
                print "firmware name:",item["firmwareName"]


