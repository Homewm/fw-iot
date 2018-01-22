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

class ipcomSpider(Spider):
    name = "ipcom"
    timeout = 20
    trytimes = 3
    start_urls = [
        #"http://www.ip-com.com.cn/en/Service.html"
        #"http://www.ip-com.com.cn/en/ce.html"(pdf file) this link is same to next ,so we don't scrapy it  \
        #other like gateway ,switch accesory not hava firmware
        "http://www.ip-com.com.cn/en/CloudWLAN-Questions.html",
        "http://www.ip-com.com.cn/en/Others-Questions.html"
    ]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    def parse(self, response):
        category = response.xpath('//div[@id="myTabContent"]/div//h3/a/@href').extract()
        for c in category:
            url = urlparse.urljoin(response.url, c)
            request = scrapy.Request(url, callback=self.parse_page)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "IP-COM"
            yield request

    def parse_page(self,response):
        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        section = response.xpath('//div[@class="container searchrow2"]')
        for s in section:
            tables = s.xpath('./div//h3/text()').extract()
            if "Firmware" in tables:
                firminfo = s.xpath('./div//div[@class="clearfix"]/dl/dd/a[1]/@href').extract()[0]
                urltmp = urlparse.urljoin(response.url, firminfo)
                fileurl = urltmp.replace("(","%28").replace(")","%29").replace(" ","%20")

                firmname = urltmp.split("/")[-1]
                print "filename:",firmname
                version = re.search("[V,v]\d\d?\.\d\.\d\.\d+",firmname)
                if version:
                    version = version.group()
                else:
                    version = ""
                print "version:",version

                publishtime = urltmp.split("_")[1]
                try:
                    array = time.strptime(publishtime, u"%Y%m%d%H%M%S")
                    item["publishTime"] = time.strftime("%Y-%m-%d", array)
                except Exception, e:
                    print e

                item["productVersion"] = version
                item["productClass"] = ""
                item["productModel"] = ""
                item["description"] = ""
                item["url"] = fileurl
                item["firmwareName"] = firmname
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                yield item
                print "firmware name:", item["firmwareName"]





