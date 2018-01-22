# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.19"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
import re
import urlparse
import urllib2
import time
# very importment!!!!!!!!!!!!!!!!!!!!!!!!!
# "firmware ftp site"
# "http://www.qno.cn/web/soft.asp -->turn to down url"
# "http://au.qno.tw/ftp/-->http://au.qno.tw/ftp/Firmware/"
class qnoSpider(Spider):
    name = "qno"
    timeout = 20
    trytimes = 3
    start_urls = [
        "http://au.qno.tw/ftp/Firmware/"
        # "http://au.qno.tw/ftp/Firmware/FQR104_32MB/"
    ]
    # must be lower character
    typefilter = ["txt", "pdf" ,"gdb"]
    allsuffix = Set()

    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_page)
        request.meta["prototype"] = MI.FirmcrawlerItem()
        request.meta["prototype"]["manufacturer"] = "QNO"
        yield request

    def parse_page(self, response):
        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        lists = response.selector.xpath('//table/tr[position()>3]')
        for l in lists:
            urlpart = l.xpath('.//a/@href').extract()
            if urlpart:
                absurl = urlparse.urljoin(response.url,urlpart[0])
                filename = urlpart[0]
                if urlpart[0].endswith('/'):
                    # print "absurl:", absurl
                    request = scrapy.Request(absurl, callback=self.parse_page)
                    request.meta["prototype"] = response.meta["prototype"]
                    yield request
                else:
                    filetype = urlpart[0].split(".")[-1].lower()
                    if filetype not in qnoSpider.typefilter:
                        version = re.search("[V,v]?\d\d?\.\d(\.\d\d?)+", filename)
                        if version:
                            version = version.group()
                        else:
                            version = ""
                        #print "version:", version
                        publishtime = l.xpath('./td[3]/text()').extract()[0].strip()
                        array = time.strptime(publishtime, u"%Y-%m-%d %H:%S")
                        item["publishTime"] = time.strftime("%Y-%m-%d", array)

                        item["productVersion"] = version
                        item["productClass"] = ""
                        item["productModel"] = ""
                        item["description"] = ""
                        item["url"] = absurl
                        item["firmwareName"] = filename
                        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        yield item
                        print "firmware name:", item["firmwareName"]
                    else:
                        print "in filter list"










