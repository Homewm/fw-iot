# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.18"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
import re
import urlparse
import urllib2
import time

class netcoreSpider(Spider):
    name = "netcore"
    timeout = 8
    trytimes = 3
    start_urls = ["http://www.netcoretec.com/software.html"]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    def parse(self, response):
        for i in xrange(1,26+1): #26+1
            url = "http://www.netcoretec.com/softwarelist/&downloadcategoryid=7&isMode=false&pageNo=%s&pageSize=10.html" %i
            request = scrapy.Request(url, callback=self.parse_list)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "net-core"
            yield request

    def parse_list(self, response):
        tables = response.xpath('//table[@id="talbeclass"]//a/@href').extract()
        for t in tables:
            url = urlparse.urljoin(response.url,t.split("'")[-4])
            request = scrapy.Request(url, callback=self.parse_page)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "net-core"
            yield request
    def parse_page(self,response):
        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        tables = response.xpath('//div[@class="con-module"]/p/a/@href').extract()
        absurl = urlparse.urljoin(response.url,tables[0])
        item["url"] = absurl
        filename = item["url"].split("/")[-1]
        item["productVersion"] = ""
        item["publishTime"] = ""
        item["productClass"] = ""
        item["productModel"] = ""
        item["description"] = ""
        item["firmwareName"] = filename
        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        yield item
        print "firmware name:",item["firmwareName"]



