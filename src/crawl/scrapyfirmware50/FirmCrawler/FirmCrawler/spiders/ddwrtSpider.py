# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.03.27"
from sets import Set
from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
import re
import urlparse
import urllib2
import time
from proxy_ips import proxy_ip
import random
import scrapy


def random_proxy_ip():
    proxy_ip_index = random.randint(0,len(proxy_ip)-1)
    res = proxy_ip[proxy_ip_index]
    return res

    #relative url
        # #"http://www.dd-wrt.com/site/support/other-downloads?path=Documentation%2F"
        # "http://www.dd-wrt.com/site/support/other-downloads"
class ddwrtSpider(Spider):
    name = "ddwrt"
    timeout = 8
    trytimes = 3
    start_urls = [
        "http://www.dd-wrt.com/site/support/other-downloads?path=betas%2F2015%2F",
        "http://www.dd-wrt.com/site/support/other-downloads?path=betas%2F2016%2F",
        "http://www.dd-wrt.com/site/support/other-downloads?path=betas%2F2017%2F",
        "http://www.dd-wrt.com/site/support/other-downloads?path=stable%2F"
    ]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    headurl = "http://www.dd-wrt.com"

    def parse(self, response):
        print "use ip"
        iprand = random_proxy_ip()
        print "random proxy:", iprand
        request = scrapy.Request(response.url, callback=self.parse_page,meta={'proxy':'http://'+iprand})
        request.meta["prototype"] = MI.FirmcrawlerItem()
        request.meta["prototype"]["manufacturer"] = "dd-wrt"
        yield request



    def parse_page(self, response):
        prototype = response.meta['prototype']
        dirs = response.xpath(
            '//table[@class="list"]/tr[position()>3]')
        for d in dirs:
            listtype = d.xpath('./td[2]/text()').extract()
            if listtype:
                urls = d.xpath('./td[1]/a/@href').extract()[0]
                #aim to "http://www.dd-wrt.com/site/support/other-downloads?path=betas%2F2012%2F03-08-12-r18687%2F?path=betas%2F2012%2F03-08-12-r18687%2Ffiles%2F"
                urlsdiv = urls.split('?path')
                if len(urlsdiv)==3:
                    urls = urlsdiv[0] + "?path" + urlsdiv[-1]
                absurl = urlparse.urljoin(ddwrtSpider.headurl,urls)
                #print "folder:",absurl
                request = scrapy.Request(absurl, callback=self.parse_page)
                request.meta["prototype"] = response.meta["prototype"]
                yield request
            else:
                urls = d.xpath('./td[1]/a/@href').extract()[0]
                absurl = urlparse.urljoin(ddwrtSpider.headurl, urls)
                publishtime = d.xpath('./td[4]/text()').extract().pop()
                filename = absurl.split('/')[-1]

                if len(filename.split('.'))!=1: #remove not filetype
                    if filename.split('.')[-1] not in ddwrtSpider.typefilter:
                        item = MI.FirmcrawlerItem(prototype)
                        item["firmwareName"] = filename
                        item["publishTime"] = publishtime
                        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        item["url"] = absurl
                        item["description"] = ""
                        item["productClass"] = "Router"
                        item["productVersion"] = ""
                        item["productModel"] = ""
                        yield item
                        print "firmware name:", item["firmwareName"]
                        return
