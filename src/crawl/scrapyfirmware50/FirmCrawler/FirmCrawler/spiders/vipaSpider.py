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

class VipaSpider(Spider):
    name = "vipa"
    timeout = 20
    trytimes = 3
    start_urls = ["http://www.vipa.com/en/service-support/downloads/firmware"]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()
    headurl = "http://www.vipa.com/"

    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_page)
        request.meta["prototype"] = MI.FirmcrawlerItem()
        request.meta["prototype"]["manufacturer"] = "Vipa"
        yield request

    def parse_page(self, response):
        lines = response.selector.xpath(
            '//div[@class="sbfolderdownload"]/div[1]/a')
        prototype = response.meta['prototype']
        dirs = response.selector.xpath(
            "//div[@id='sbfolderFolderWrap']/div[@class='sbfolderFolder']/a/@href").extract()

        for i in dirs:
            absurl = urlparse.urljoin(VipaSpider.headurl,i)
            request = scrapy.Request(absurl, callback=self.parse_page)
            request.meta["prototype"] = response.meta["prototype"]
            yield request

        for a in lines:
            filename = a.xpath("text()").extract().pop()
            filetype = filename.rsplit(".", 1).pop().strip().lower()
            VipaSpider.allsuffix.add(filetype)
            if not filetype in VipaSpider.typefilter:
                item = MI.FirmcrawlerItem(prototype)
                item["productVersion"]=""
                item["publishTime"]=""
                item["productClass"]=""
                item["productModel"]=""
                item["description"]=""
                url = response.urljoin(
                    a.xpath("@href").extract().pop())
                item["url"]=url.replace(" ","%20")
                item["firmwareName"] = filename
                item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                #item["Title"] = item["Filename"]
                item["description"] = str().join(
                    a.xpath("//div[@class='up']//text()").extract())



                #divide version
                try:
                    #ss1 = ["FEE0","3Bxxx"]
                    #ss2 = ["Bb000082","BB000088","BB000090","BB000021"]
                    m = filename.split("_")
                    #针对CPU314SE_V3502.zip
                    likeStand= m[-1].replace(".zip","").replace(".bin","").replace(".BIN","").replace(".os","").replace(".WEC","")
                    # aim at  Px000008_V208_CPU.zip  or  CP 208-1DP01_V522_a2.zip
                    if likeStand in ["DP","CPU","CP","image","a1","a2","a3"]:
                        likeStand = m[-2]
                    if likeStand in ["Tool","CXX"]:
                        likeStand = ""
                    #Special case:
                    if likeStand=="OLD V111 HW V1.0":
                        likeStand = "V1.0"
                    # Special case:
                    if likeStand == "IM208":
                        likeStand = "V419"
                    if likeStand in ["DEMO"]:
                        if filename.split("_")[-2].split("-")[0] in ["ZENON"]:
                            likeStand = filename.split("_")[-2].split("-")[1]
                    #aim at WinCE-5.0_520MHz_PROF-09-01-15_ZENON-6.22-SP0-B6.zip
                    likeStand1 = likeStand.split("-")[0]
                    if likeStand1 in ["M","MOV","ZENON"]:
                        likeStand = likeStand.split("-")[1]
                    if likeStand1 in ["CORE", "PROF"]:
                        likeStand = ""

                    #aim at BB000021.214
                    likeStand2 = likeStand.split(".")[0]
                    if likeStand2 in ["Bb000082","BB000088","BB000090","BB000021","Bb000125"]:
                        likeStand = ""
                    #remove
                    if m[0]=="MicroSD":
                        likeStand = ""
                    item["productVersion"] = likeStand


                    item["productModel"] = item["URL"].split("/")[6].replace('%20', " ").strip()
                    Controlsystem = ["System 300S","System 100V","System 200V","System 300V","System 400V","System 500S","System 500V"]
                    Sliosystem = ["System Slio"]
                    Hmi = ["HMI"]
                    Netcomponents = ["Components"]
                    Zubehor=["Zubehör"]
                    if item["productModel"] in Netcomponents:
                        item["productClass"]= "Netcomponents"
                    elif item["productModel"] in Sliosystem:
                        item["productClass"]= "Sliosystem"
                    elif item["productModel"] in Hmi:
                        item["productClass"]= "Hmi"
                    elif item["productModel"] in Controlsystem:
                        item["productClass"]= "Controlsystem"
                    elif item["productModel"] in Zubehor:
                        item["productClass"] = "Zubehör"
                    else:
                        item["productClass"]= ""
                except:
                    pass
                yield item
                print "firmwarename:",item["firmwareName"]
        #print "all suffix:",VipaSpider.allsuffix
        return