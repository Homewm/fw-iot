from scrapy import Spider
from scrapy.http import Request

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader

import urlparse
import time
import scrapy


from proxy_ips import proxy_ip
import random


def random_proxy_ip():
    proxy_ip_index = random.randint(0,len(proxy_ip)-1)
    #res = {'http':proxy_ip[proxy_ip_index]}
    res = proxy_ip[proxy_ip_index]
    return res
class PolycomSpider(Spider):
    name = "polycom"
    allowed_domains = ["polycom.com"]
    start_urls = ["http://support.polycom.com/PolycomService/support/us/support/video/index.html", "http://support.polycom.com/PolycomService/support/us/support/voice/index.html", "http://support.polycom.com/PolycomService/support/us/support/network/index.html",
                  "http://support.polycom.com/PolycomService/support/us/support/cloud_hosted_solutions/index.html", "http://support.polycom.com/PolycomService/support/us/support/strategic_partner_solutions/index.html"]

    download = "/PolycomService/support/us"

    @staticmethod
    def fix_url(url):
        if "://" not in url:
            return PolycomSpider.download + url
        return url

    def parse(self, response):
        print "use ip"
        iprand = random_proxy_ip()
        print "random proxy:", iprand
        request = scrapy.Request(response.url, callback=self.parse_page,meta={'proxy':'http://'+iprand})
                                 #meta={'proxy': 'http://' + '196.201.146.17:8083'} #germany
        yield request

    def parse_page(self, response):
        print "pass ip"
        if response.xpath("//form[@name='UCagreement']"):
            for href in response.xpath(
                    "//div[@id='productAndDoc']").extract()[0].split('"'):
                if "downloads.polycom.com" in href:
                    item = FirmcrawlerItem()
                    item["productVersion"] = response.meta["version"]
                    item["publishTime"] = response.meta["date"]
                    item["productClass"] = ""
                    item["productModel"] = response.meta["product"]
                    item["description"] = response.meta["description"]
                    item["url"] = href.encode("utf-8")
                    item["firmwareName"] = item["url"].split('/')[-1]
                    item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    item["manufacturer"] = "polycom"
                    yield item
                    print "firmware name:", item["firmwareName"]


        elif response.xpath("//div[@id='ContentChannel']"):
            for entry in response.xpath("//div[@id='ContentChannel']//li"):
                if not entry.xpath("./a"):
                    continue

                text = entry.xpath("./a//text()").extract()[0]
                href = entry.xpath("./a/@href").extract()[0].strip()
                date = entry.xpath("./span//text()").extract()

                path = urlparse.urlparse(href).path

                if any(x in text.lower() for x in ["end user license agreement", "eula", "release notes",
                                                   "mac os", "windows", "guide", "(pdf)", "sample"]) or href.endswith(".pdf"):
                    continue

                elif any(path.endswith(x) for x in [".htm", ".html"]) or "(html)" in text.lower():
                    yield Request(
                        url=urlparse.urljoin(
                            response.url, PolycomSpider.fix_url(href)),
                        meta={"product": response.meta["product"] if "product" in response.meta else text,
                              "date": date, "version": FirmwareLoader.find_version_period([text]), "description": text},
                        headers={"Referer": response.url},
                        callback=self.parse_page)

                elif path:
                    item = FirmcrawlerItem()
                    item["productVersion"] = FirmwareLoader.find_version_period([text])
                    item["publishTime"] = FirmwareLoader(date_fmt=["%Y-%m-%d"]).find_date(date)
                    item["productClass"] = ""
                    item["productModel"] = response.meta["product"]
                    item["description"] = text
                    item["url"] = href.encode("utf-8")
                    item["firmwareName"] = item["url"].split('/')[-1]
                    item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    item["manufacturer"] = "polycom"
                    yield item
                    print "firmware name:", item["firmwareName"]


