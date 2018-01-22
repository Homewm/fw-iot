# -*- coding: UTF-8 -*-
__author__ = "zhaoweiwei"
__time__ = "2017.04.12"
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


def random_proxy_ip():
    proxy_ip_index = random.randint(0,len(proxy_ip)-1)
    #res = {'http':proxy_ip[proxy_ip_index]}
    res = proxy_ip[proxy_ip_index]
    return res
class VipaSpider(Spider):
    name = "dji"
    timeout = 20
    trytimes = 3
    start_urls = ["http://www.dji.com/products/drones#consumer-nav"]
    typefilter = ["txt", "pdf"]
    allsuffix = Set()


    def parse(self, response):
        iprand = random_proxy_ip()
        print "random proxy:", iprand
        request = scrapy.Request(response.url, callback=self.parse_list,meta={'proxy':'http://'+iprand})
        yield request

    def parse_list(self,response):
        lists = response.xpath('//div[@id="scroll-content"]/section/div[@class="row"]/ul/li/a[1]/@href').extract()
        print "xian list len:",len(lists)
        for l in lists:

            if (l == "http://www.dji.com/cn/phantom-3-se"):
                print "wei se"
            else:
                request = scrapy.Request(l, callback=self.parse_download)
                yield request
        print "list len:",len(lists)

    def parse_download(self,response):


        downloadurl = response.xpath('//div[@class="container-sub-nav"]/div[@id="subNavBar"]/ul[@class="navbar-nav navbar-right sub-nav-right"]/li[3]/a/@href').extract()
        if downloadurl:
            downloadurl = downloadurl[0]
        else:
            return
        #downloadurl = response.url + "/info#downloads"
        #print "download url:",downloadurl
        request = scrapy.Request(downloadurl, callback=self.parse_page)
        yield request
    def parse_page(self,response):
        print "parse page url:",response.url

        firmwarelist = response.xpath('//div[@class="downloads-container select-list"]/div[1]/div[1]/div/ul/li')
        for ff in firmwarelist:
            firmurl = ff.xpath('./div[2]/div[1]/a/@href').extract()
            if firmurl:
                firmurl = firmurl[0]
            else:
                continue
            firmname = firmurl.split('/')[-1]

#"Installer": software (yes)
#"Driver":qudong     (no) (because some driver run in pc or equipment,in order to have a general standard,we dont get it)

#"Assistant" ,tiao can software ,but you need del "发布记录"(no)
# "GL" Phantom 4 Pro+ 遥控器固件升级包 v01.02.00.00 (yes)  http://www.dji.com/cn/phantom-4-pro/info#downloads
# " How" (no)  https://dl.djicdn.com/downloads/phantom_4_pro/20170307/How_to_Update_the_Remote_Controller_Firmware_of_Phantom_4_Pro_plus_CN.zip
#
#

            if any(item in firmname for item in ("FW","Firmware","RC","firmware","Installer","installer","Assistant","GL")) and \
                    not any(item in firmname for item in ("Guide","guide","Instruction","Tool","Cleaner","Driver",u"发布记录","How")):

                firmname = firmurl.split('/')[-1]
                publishtime = ff.xpath('./div[1]/div[2]/text()').extract()[0]
                # info = ff.xpath('./div[1]/div[1]/text()').extract()[0]
                # model = info.split('Firmware')[0].strip()
                # version = info.split('Firmware')[-1].strip()

                item = MI.FirmcrawlerItem()
                item["productVersion"] = ""
                item["publishTime"] = publishtime
                item["productClass"] = "UAV"
                item["productModel"] = ""
                item["description"] = ""
                item["url"] = firmurl
                item["firmwareName"] = firmname
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                item["manufacturer"] = "dji"
                yield item
                print "firmware name:", item["firmwareName"]
            #else:
                #print "error???????????????????????????????????????????/",response.url



