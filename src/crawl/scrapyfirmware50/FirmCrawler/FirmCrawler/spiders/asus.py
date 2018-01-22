from scrapy import Spider
from scrapy.http import Request

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader
import urlparse
import time


class AsusSpider(Spider):
    name = "asus"
    region = "en"
    allowed_domains = ["asus.com"]
    start_urls = ["https://www.asus.com/support/"]

    visited = []

    def parse(self, response):
        if "cid" not in response.meta:
            for category in response.xpath("//div[@class='product-category']//a/@l1_id").extract():
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s" % (self.region, category)),
                    meta={"cid": category},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse)

        elif "sid" not in response.meta:
            for series in response.xpath("//table/id/text()").extract():
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s&s=%s" % (self.region, response.meta["cid"], series)),
                    meta={"cid": response.meta["cid"], "sid": series},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse)

        elif "product" not in response.meta:
            for prod in response.xpath("//table"):
                pid = prod.xpath("./l3_id/text()").extract()[0]
                product = prod.xpath("./m_name/text()").extract()[0]
                mid = prod.xpath("./m_id/text()").extract()[0]

                # choose "Others" = 8
                yield Request(
                    url=urlparse.urljoin(response.url, "/support/Download/%s/%s/%s/%s/%d" % (response.meta["cid"], response.meta["sid"], pid, mid, 8)),
                    meta={"product": product},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse_product)

    def parse_product(self, response):
        # types: firmware = 20, gpl source = 30, bios = 3
        for entry in response.xpath(
                "//div[@id='div_type_20']/div[@id='download-os-answer-table']"):
            item=FirmcrawlerItem()

            version = FirmwareLoader.find_version_period(
                entry.xpath("./p//text()").extract())
            gpl = None

            # grab first download link (e.g. DLM instead of global or p2p)
            href = entry.xpath("./table//tr[3]//a/@href").extract()[0]
            print "href:",href


            item["productVersion"] = version
            item["publishTime"] = entry.xpath("./table//tr[2]/td[1]//text()").extract()[-2]
            item["productClass"] = ""
            item["productModel"] = response.meta["product"]
            item["description"] = " ".join(entry.xpath("./table//tr[1]//td[1]//text()").extract()).strip()
            item["url"] = href
            item["firmwareName"] = href.split('/')[-1]
            item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["manufacturer"] = "asus"
            yield item


