# -*- coding: UTF-8 -*-
__author__="zhangguodong"
__time__ = "20170331"
from scrapy.spiders import Spider
import re
import scrapy
import time
import os
import os.path
import urlparse,urllib,urllib2
# import logging
# import hashlib
from sets import Set
from scrapy.spiders import Spider
import FirmCrawler.items as MI
# from FirmCrawler import *
from proxy_ips import proxy_ip
import random


def random_proxy_ip():
    proxy_ip_index = random.randint(0,len(proxy_ip)-1)
    #res = {'http':proxy_ip[proxy_ip_index]}
    res = proxy_ip[proxy_ip_index]
    return res
class DahuaSpider(Spider):
    name = "dahua"
    timeout = 20
    trytimes = 3
    start_urls = {"http://download.dahuatech.com/kit.php"}
    suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip", "ipk",
              "bz2", "BIN", "gz", "7z", "lzma", "tgz", "exe", "ZIP", "tar", "ubi",
              "uimage", "rtf", "ram", "elf", "ipa", "chm", "dsw", "dsp", "clw", "mav",
              "dav", "upg", "bfp", "hex", "npk"]
    headurl="http://download.dahuatech.com"

    def parse(self,response):
        iprand = random_proxy_ip()
        print "random proxy:", iprand
        request=scrapy.Request(response.url, callback=self.parse_first,meta={'proxy':'http://'+iprand})
        yield request

    def parse_first(self,response):
        #hrefs= response.selector.xpath('//div[@class="download_body"]/ul[1]/li[position()>1]/div/a/@href').extract()
        hrefs= response.selector.xpath('//div[@class="download_body"]/ul[1]/li[position()>1]/div/a/@href').extract()

        for href in hrefs:
            absoluteurl = urlparse.urljoin(DahuaSpider.headurl, href)
            # print "url:",absoluteurl
            request = scrapy.Request(absoluteurl, callback=self.parse_second)
            yield request

    def parse_second(self, response):
        hrefs = response.selector.xpath('//div[@class="tools_body mrgB50"]/ul/li/a/@href').extract()
        for href in hrefs:
            absoluteurl = urlparse.urljoin(DahuaSpider.headurl, href)
            #print "parse second url:",absoluteurl
            # print "second url:",absoluteurl
            request = scrapy.Request(absoluteurl, callback=self.parse_third)
            yield request
        return

    def parse_third(self, response):
        #print "parse third"
        tables = response.selector.xpath('//div[@class="kit_det_body"]/table')
        for table in tables:
            dataurl = table.xpath('./tr[1]/td[2]/a/@data').extract()[0]


            filename = dataurl.split("=",1)[-1]
            absoluteurl = "http://download.dahuatech.com/kitDownload.php?filepath=" + filename
            version = filename.split('_')[-1].rsplit('.',1)[0]
            model = filename.split('_')[1]
            item = MI.FirmcrawlerItem()
            item["productVersion"] = version
            item["publishTime"] = ""
            item["productClass"] = "Camera"
            item["productModel"] = model
            item["description"] = ""
            item["url"] = absoluteurl
            item["firmwareName"] = filename
            item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["manufacturer"] = "dahua"
            yield item
            print "firmware name:",item["firmwareName"]


            
