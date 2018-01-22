# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.13"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
import re
import urlparse
import urllib2
import time

class volansSpider(Spider):
    name = "volans"
    timeout = 12
    trytimes = 3
    start_urls = [
        "http://www.adslr.com/down/gjxz/index.html",
        "http://www.adslr.com/down/gjxz/index_2.html"
    ]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_list)
        yield request

    def parse_list(self, response):
        tables = response.xpath('//div[@class="content"]//a/@href').extract()
        for t in tables:
            absurl = urlparse.urljoin(response.url,t)
            request = scrapy.Request(absurl, callback=self.parse_page)
            yield request
    def parse_page(self,response):
        urls = response.xpath('//div[@id="right"]/ul/table/tr[2]/td[2]//a/@href').extract()
        absurl = urlparse.urljoin(response.url,urls[0])
        filename = absurl.split("/")[-1]
        model = response.xpath('//div[@id="right"]/ul/table/tr[1]/td[2]//text()').extract().pop()
        publishtime = response.xpath('//div[@id="right"]/ul/table/tr[5]/td[2]//text()').extract().pop()
        desc = response.xpath('//div[@id="right"]/ul/table/tr[6]/td[2]//text()').extract()
        item = MI.FirmcrawlerItem()
        item["productVersion"] = ""
        item["productClass"] = "Router"
        item["productModel"] = model
        item["description"] = str().join(desc).strip()
        item["url"] = absurl
        item["firmwareName"] = filename
        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        item["manufacturer"] = "volans"
        try:
            array = time.strptime(publishtime, u"%Y-%m-%d %H:%M:%S")
            item["publishTime"] = time.strftime("%Y-%m-%d", array)
        except Exception, e:
            print e
        yield item
        print "firmware name:", item["firmwareName"]
