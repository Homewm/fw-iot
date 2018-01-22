from scrapy import Spider
from scrapy.http import Request

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader

import urlparse
import time

# http://www.fiosfaq.com/index.php?action=cat&catnum=12
# http://verizontest.blogspot.com/p/general-info.html
# https://github.com/jameshilliard/jungo-image

# https://upgrade.actiontec.com/MI424WR/MI424WR.rmt
# https://upgrade.actiontec.com/MI424WR2/MI424WR2.rmt
# https://upgrade.actiontec.com/MI424WR2/MI424WR_D.rmt
# https://upgrade.actiontec.com/MI424WR2/MI424WR_EF.rmt
# https://upgrade.actiontec.com/MI424WR2/MI424WR_G.rmt
# https://upgrade.actiontec.com/MI424WR-GEN3I/MI424WR-GEN3I.rmt

class VerizonSpider(Spider):
    name = "verizon"
    allowed_domains = ["verizon.com"]
    start_urls = [
        "http://my.verizon.com/micro/fiosrouters/",
        "https://www.verizon.com/Support/Residential/internet/highspeed/troubleshooting/network/firmwareupgrade/123451.htm"
        ]

    def parse(self, response):
        if response.xpath("//select[@id='router']"):
            for product in response.xpath(
                    "//select[@id='router']/option/@value").extract():
                if product and product != "allrouters":
                    yield Request(
                        url=urlparse.urljoin(
                            response.url, "?router=%s" % (product)),
                        headers={"Referer": response.url},
                        callback=self.parse)

        elif response.xpath("//td[@id='search_main_content']"):
            for link in response.xpath("//td[@id='search_main_content']//a"):
                if link.xpath("./@href"):
                    href = link.xpath("./@href").extract()[0]
                    text = link.xpath(".//text()").extract()

                    if "download.verizon.net" in href and "firmware" in href:
                        item = FirmcrawlerItem()
                        item["productVersion"] = ""
                        item["publishTime"] = ""
                        item["productClass"] = ""
                        item["productModel"] = ""
                        item["description"] = text[0]
                        item["url"] = href
                        item["firmwareName"] = href.split('/')[-1]
                        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        item["manufacturer"] = "verizon"
                        yield item
                        print "firmware name:", item["firmwareName"]

        else:
            for link in response.xpath("//div[@id='ghfbodycontent']//a"): #url1 turn to page
                if link.xpath("./@href"):
                    href = link.xpath("./@href").extract()[0]
                    text = link.xpath(".//text()").extract()

                    if "download.verizon.net" in href and "firmware" in href:
                        item = FirmcrawlerItem()
                        item["productVersion"] = ""
                        item["publishTime"] = ""
                        item["productClass"] = ""
                        item["productModel"] = ""
                        item["description"] = text[0]
                        item["url"] = href
                        item["firmwareName"] = href.split('/')[-1]
                        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        item["manufacturer"] = "verizon"
                        yield item
                        print "firmware name:", item["firmwareName"]

