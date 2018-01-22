from scrapy import Spider

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader
import time
import urlparse
import scrapy

class SupermicroSpider(Spider):
    name = "supermicro"
    allowed_domains = ["supermicro.com"]
    start_urls = [
        "http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=1",
        "http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=2",
        #"http://supermicro.com/support/bios/archive.cfm" #because it's complex ,so don't do it
    ]


    @staticmethod
    def fix_url(url):
        if "url=" in url:
            return url[url.find('=') + 1:]
        return url

    def parse(self, response):
        for i in xrange(1,13+1):
            url = "http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=1&page=%s" % i
            request = scrapy.Request(url, callback=self.parse_page)
            yield request
        for j in xrange(1,2+1):
            url2 = "http://supermicro.com/ResourceApps/BIOS_IPMI.aspx?MoboType=2&page=%s" %j
            request = scrapy.Request(url2, callback=self.parse_page)
            yield request


    def parse_page(self,response):
        if response.xpath(
                "//table[@id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderSupportMiddle_Table_REC']"):
            for row in response.xpath(
                    "//table[@id='ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderSupportMiddle_Table_REC']/tr[position() > 1]"):
                product = row.xpath(".//td[1]//text()").extract()[0]
                rev = row.xpath(".//td[3]//text()").extract()[0]
                href = row.xpath(".//td[4]//a/@href").extract()
                if href:
                    href = href[0]
                else:
                    return
                filename = row.xpath(".//td[4]//a/text()").extract()[0]
                url = urlparse.urljoin(response.url,SupermicroSpider.fix_url(href))
                item = FirmcrawlerItem()
                item["productVersion"] = rev
                item["publishTime"] = ""
                item["productClass"] = ""
                item["productModel"] = product
                item["description"] = ""
                item["url"] = url
                item["firmwareName"] = filename
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                item["manufacturer"] = "supermicro"
                yield item
                print "firmware name:", item["firmwareName"]
        else:
            for row in response.xpath(
                    "//table//table//table//table//table//tr[position() > 1]"):
                product = row.xpath(".//td[1]//text()").extract()[0]
                href = row.xpath(".//td[2]//a/@href").extract()[0]
                rev = row.xpath(".//td[4]//text()").extract()[0]
                filename = row.xpath(".//td[4]//a/text()").extract()[0]
                url = urlparse.urljoin(response.url, SupermicroSpider.fix_url(href))
                item = FirmcrawlerItem()
                item["productVersion"] = rev
                item["publishTime"] = ""
                item["productClass"] = ""
                item["productModel"] = product
                item["description"] = ""
                item["url"] = url
                item["firmwareName"] = filename
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                item["manufacturer"] = "supermicro"
                yield item
                print "firmware name:",item["firmwareName"]
