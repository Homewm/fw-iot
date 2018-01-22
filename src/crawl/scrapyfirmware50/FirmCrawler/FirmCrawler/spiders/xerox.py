from scrapy import Spider
from scrapy.http import Request

from FirmCrawler.items import FirmcrawlerItem
from FirmCrawler.loader import FirmwareLoader
import scrapy
import urlparse
import time
from proxy_ips import proxy_ip
import random


def random_proxy_ip():
    proxy_ip_index = random.randint(0,len(proxy_ip)-1)
    #res = {'http':proxy_ip[proxy_ip_index]}
    res = proxy_ip[proxy_ip_index]
    return res
class XeroxSpider(Spider):
    name = "xerox"
    allowed_domains = ["xerox.com"]
    start_urls = [
        "http://www.support.xerox.com/dnd/productList.jsf?Xlang=en_US"]

    def parse(self, response):
        iprand = random_proxy_ip()
        print "random proxy:", iprand
        request = scrapy.Request(response.url, callback=self.parse_list, meta={'proxy': 'http://' + iprand})
        yield request
    def parse_list(self,response):

        for href in response.xpath(
                "//div[@class='productResults a2z']//a/@href").extract():
            if "downloads" in href:
                durl = urlparse.urljoin(response.url, href)
                request = scrapy.Request(durl,callback=self.parse_download)
                yield request

    def parse_download(self, response):
        print response.url
        for firmware in response.xpath(
                "//li[@class='categoryBucket categoryBucketId-7']/ul/li"):
            product = response.xpath(
                "//div[@class='prodNavHeaderBody']//text()").extract()[0].replace(" Support & Drivers", "")
            date = firmware.xpath(
                ".//ul[@class='dateVersion']/li[1]/strong/text()").extract()[0]
            publishtime = ""
            try:
                #May 13, 2010
                array = time.strptime(date, u"%b %d, %Y")
                publishtime = time.strftime("%Y-%m-%d", array)
            except Exception, e:
                print e
            version = firmware.xpath(
                ".//ul[@class='dateVersion']/li[2]/strong/text()").extract()
            print "version:",version
            href = firmware.xpath(
                ".//a/@href").extract()[0].replace("file-download", "file-redirect")

            absurl = urlparse.urljoin(response.url,href)
            print "href:", href
            text = firmware.xpath(".//a//text()").extract()[0]
            print "text:",text
            filename = firmware.xpath("./div[2]/h4/a/text()").extract()[0]
            print "filename:", filename

            item = FirmcrawlerItem()
            item["productVersion"] = FirmwareLoader(date_fmt=["%Y-%m-%d"]).find_version_period(version)
            item["publishTime"] = publishtime
            item["productClass"] = "printer"
            item["productModel"] = product
            item["description"] = text
            item["url"] = absurl
            item["firmwareName"] = filename
            item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["manufacturer"] = "xerox"
            yield item
            print "firmware name:", item["firmwareName"]




