# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.13"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import re
import urlparse
import FirmCrawler.items as MI
import urllib2
import time

class tendaSpider(Spider):
    name = "tenda"
    timeout = 12
    trytimes = 3
    start_urls = [
        "http://www.tenda.com.cn/service/download-cata-11.html"
    ]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_list)
        yield request

    def parse_list(self, response):
        print response.url
        #tables = response.xpath('//div[@class="col-sm-12 col-md-8"]/dl//a/@href').extract()  2017.07.20 lose efficacy, begin location
        tables = response.xpath('//div[@class="Downnewbox  clearfix"]/div/a/@href').extract()
        print len(tables)
        for t in tables:
            absurl = urlparse.urljoin(response.url,t)
            request = scrapy.Request(absurl, callback=self.parse_page)
            yield request
    def parse_page(self,response):
        #print response.url
        urls = response.xpath('//div[@class="ddart clearfix"]/a/@href').extract()[0]
        absurl = urls.replace("(","%28").replace(")","%29")
        filename = urls.split("/")[-1]
        filename = unicode.encode(filename,encoding='utf-8')

        infos = response.xpath('//div[@class="ddart clearfix"]/div[1]/h1/text()').extract().pop()
        infos = unicode.encode(infos,encoding='utf8')
        model = infos.split(r"升级软件")[0]
        version =infos.split(r"升级软件")[-1].strip()
        #publishtime = response.xpath('//div[@id="sumdes"]/span[1]/span/text()').extract().pop()  2017.0720 no publishtime
        desc = response.xpath('//div[@class="ddart clearfix"]/div[2]/p[1]/text()').extract()
        item = MI.FirmcrawlerItem()
        item["productVersion"] = version
        item["productClass"] = ""
        item["productModel"] = model
        item["description"] = str().join(desc).strip()
        item["url"] = absurl
        item["firmwareName"] = filename
        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        item["manufacturer"] = "tenda"
        item["publishTime"] = ""
        # try:
        #     array = time.strptime(publishtime, u"%Y/%m/%d %H:%M:%S")
        #     item["publishTime"] = time.strftime("%Y-%m-%d", array)
        # except Exception, e:
        #     print e
        yield item
        print "firmware name:", item["firmwareName"]
