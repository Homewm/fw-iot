#_*_ coding:utf-8 _*_
__author__ = "zhangguodong"
__time__ = "2017.04.12"


from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
from sets import Set
import time
import urlparse
import re

class WayosSpider(Spider):
    name = "wayos"
    allowed_domain = ["wayos.com"]
    start_urls = [
        "http://www.wayos.com/download/firmware/list_30_1.html",
    ]
    # headurl= "http://www.wayos.com"
    allsuffix = Set()
    timeout = 8
    trytimes = 3

    def parse(self, response):
        for page in xrange(1,47):
            url = "http://www.wayos.com/download/firmware/list_30_" + str(page) + ".html"
            # print url
            request = scrapy.Request(url, callback=self.parse_list)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "Wayos"
            yield request

    def parse_list(self,response):
        hrefs = response.selector.xpath('//div[@class="listbox"]//span/a/@href').extract()
        # print url
        for href in hrefs:
            absurl = urlparse.urljoin(response.url,href)
            # print absurl
            request = scrapy.Request(absurl, callback=self.parse_second)
            request.meta["prototype"] = response.meta["prototype"]
            yield request

    def parse_second(self,response):
        itemurl = response.selector.xpath('//div[@class="infolist"]/span[6]/li/a/@href').extract()
        if itemurl:
            itemurl.pop()
        else:
            return
        absurl = urlparse.urljoin(response.url, itemurl)
        filename = response.selector.xpath('//div[@class="article-bd"]/h1/text()').extract()
        filename = str().join(filename)
        filename = unicode.encode(filename,encoding='utf-8')

        # model
        if re.match(r'^([a-zA-Z]{0,8}\-[0-9a-zA-Z]{0,5}).*?', filename):
            Productmodel = re.match(r'^([a-zA-Z]{0,8}\-[0-9a-zA-Z]{0,5}).*?', filename).group(0)
        else:
            Productmodel = ""

        #version
        # vers = re.match(r'^([0-9a-zA-Z]{0,8}.*?[0-9]{0,5}\.[0-9]{0,5}\.[0-9a-zA-Z]{0,8}.*?', filename).group(0)
        # print vers

        publishTime = response.selector.xpath('//div[@class="infolist"]/span[3]/text()').extract().pop()
        # print publishTime
        desc = response.selector.xpath('//div[@class="content"]/text()').extract()
        desc =str().join(desc)

        prototype = response.meta['prototype']
        item = MI.FirmcrawlerItem(prototype)
        item["firmwareName"] = filename
        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        item["url"] = absurl
        item["publishTime"] = publishTime
        item["description"]  = desc
        item['productModel'] = Productmodel
        item["productVersion"] = ""


        #classify
        if r"路由" in filename:
            # print "include route"
            item["productClass"] = "Router"
        elif r"交换机" in filename:
            item["productClass"] = "Switch"
        elif r"网关" in filename:
            item["productClass"] = "Gateway"
        else:
            item["productClass"] = ""

        yield item
        print "firmware name:",item["firmwareName"]
        return











