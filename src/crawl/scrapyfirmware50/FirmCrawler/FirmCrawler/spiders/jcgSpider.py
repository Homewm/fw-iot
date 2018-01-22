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

class jcgSpider(Spider):
    name = "jcg"
    timeout = 20
    trytimes = 3
    start_urls = ["http://www.jcgcn.com/service/download/index.html"]
    # must be lower character
    typefilter = ["txt", "pdf", "apk"]
    allsuffix = Set()
    def parse(self, response):
        for i in xrange(1,10+1): #10+1
            url = "http://www.jcgcn.com/service/download/index_%s.html" %i
            if i == 1:
                url = "http://www.jcgcn.com/service/download/index.html"
            print "url:",url
            request = scrapy.Request(url, callback=self.parse_list)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "JCG"
            yield request

    def parse_list(self, response):
        tables = response.xpath('//div[@class="row down-list  service-none-type"]/ul/li')
        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        for t in tables:
            url1 = t.xpath('./div[@class="item-txt"]/a/@href').extract()
            absurl = urlparse.urljoin(response.url, url1[0])
            filename = absurl.split("/")[-1]
            filetype = filename.split(".")[-1]
            if filetype not in jcgSpider.typefilter:
                item["productVersion"] = ""
                item["publishTime"] = ""
                item["productClass"] = ""
                item["productModel"] = ""
                item["description"] = ""
                item["url"] = absurl
                item["firmwareName"] = filename
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                yield item
                print "firmware name:", item["firmwareName"]


