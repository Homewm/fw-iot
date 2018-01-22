# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.11"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
import re
import urlparse
import urllib2
import time

class schnerderSpider(Spider):
    name = "schneider"
    timeout = 20
    trytimes = 3
    start_urls = [
        "http://www.schneider-electric.com/en/download/search/?docTypeGroup=3541958-Software%2FFirmware&category=26055606-PLC%2C+PAC+and+Dedicated+Controllers"
    ]
    # must be lower character
    typefilter = ["txt", "pdf"] #,"htm"
    allsuffix = Set()
    def parse(self, response):
        for i in xrange(1,28+1):
            url = "http://www.schneider-electric.cn/zh/download/search/?docTypeGroup=4868253-%E8%BD%AF%E4%BB%B6%2F%E5%9B%BA%E4%BB%B6&" + "pageNumber=%s" %i
            print "url:",url
            request = scrapy.Request(url, callback=self.parse_list)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "schneider"
            yield request

    def parse_list(self, response):
        tables = response.xpath('//li[@class="single-result"]/h3/a/@href').extract()
        for t in tables:
            url = urlparse.urljoin(response.url,t)
            request = scrapy.Request(url, callback=self.parse_page)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "schneider"
            yield request
    def parse_page(self,response):
        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        filedownloadlist = response.xpath('//div[@class="description-download lg"]/ul[@class="list-files"]/li/a/@href').extract()
        for f in filedownloadlist:
            filename = f.split('p_File_Name=')[-1].split('&')[0]
            filetype = filename.rsplit('.',1)[-1]
            if filetype not in schnerderSpider.typefilter:
                url = f
                model = filename.split('_')[0]
                publishtime = response.xpath('//ul[@class="detail"]/li[4]/p/text()').extract().pop()
                version = response.xpath('//ul[@class="detail"]/li[5]/p/text()').extract().pop()
                desc = response.xpath('//div[@class="description-download lg"]/p[1]//text()').extract()
                try:
                    array = time.strptime(publishtime, u"%d/%m/%Y")
                    item["publishTime"] = time.strftime("%Y-%m-%d", array)
                except Exception, e:
                    print e
                item["productVersion"] = version
                item["productClass"] = ""  # more class
                item["productModel"] = model
                item["description"] = str().join(desc).strip().replace(" ","").replace('\n',"").replace('\t',"")
                item["url"] = url
                item["firmwareName"] = filename
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                yield item
                print "firmware name:",item["firmwareName"]
        return

