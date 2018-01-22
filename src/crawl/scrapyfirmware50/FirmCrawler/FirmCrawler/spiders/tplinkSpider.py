#_*_ coding:utf-8 _*_
__author__ = "zhaoweiwei"
__time__ = "2017.03.28"


from scrapy.spiders import Spider
import scrapy
import FirmCrawler.items as MI
from sets import Set
import time
import urlparse
import re

class TplinkSpider(Spider):
    name = "tplink"
    allowed_domain = ["tp-link.com.cn"]
    start_urls = [
        "http://service.tp-link.com.cn/list_download_software_1_0.html",
    ]
    # must be lower character
    suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip","ipk","bz2","BIN","gz","7z","lzma","tgz","exe","ZIP","tar","ubi","uimage","rtf","ram","elf","ipa","chm","dsw","dsp","clw","mav","dav","DAV","Dav","iso"]
    allsuffix = Set()
    timeout = 8
    trytimes = 3
    # classify seek model web page http://www.tp-link.com.cn/search.html?keywords=TL-IPC&x=0&y=0
    router = ["TL-WR", "TL-R1", "TD-W8", "TL-MR", "TL-WV", "TL-WD", "TL-ER", "TL-TR", "TL-H2", "TL-CP", "TL-PW",
              "TL-H3", "TL-H6", "TL-R4", "TL-H1"]

    modem = ["TD-89", "TD-86", "TD-88", "TD-87", "TL-GP", "TL-EP"]

    camera = ["TL-SC", "TL-IP", "TL-NV"]

    switch = ["TL-SG", "TL-SL"]

    ap = ["TL-WA", "TL-AC", "TL-AP"]

    printing_server = ["TL-PS"]

    NetworkTVBox = ["TP"]

    def parse(self, response):
        for page in xrange(1,102): #total page is 101
            url = "http://service.tp-link.com.cn/list_download_software_" + str(page) + "_0.html"
            request = scrapy.Request(url, callback=self.parse_list)
            request.meta["prototype"] = MI.FirmcrawlerItem()
            request.meta["prototype"]["manufacturer"] = "TP-LINK"
            yield request

    def parse_list(self,response):
        lists = response.selector.xpath('//table[@id="mainlist"]//a/@href').extract() #the "//" in xpath is stand some steps but not sure
        for list in lists:
            absurl = urlparse.urljoin(response.url,list) #base url equals response.url
            request = scrapy.Request(absurl, callback=self.parse_page)
            request.meta["prototype"] = response.meta["prototype"]
            yield request

    def parse_page(self,response):
        itemurl = response.selector.xpath('//div[@class="download"]/table/tr[5]/td[2]/a/@href').extract()
        if itemurl:
            itemurl = itemurl.pop()
        else:
            return
        absurl = urlparse.urljoin(response.url,itemurl)
        filetype = absurl.rsplit(".",1).pop().strip().lower()
        TplinkSpider.allsuffix.add(filetype)
        if filetype in TplinkSpider.suffix:
            prototype = response.meta['prototype']
            item = MI.FirmcrawlerItem(prototype)
            item["firmwareName"] = unicode.encode(absurl.rsplit("/",1).pop(),encoding='utf-8')
            item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["url"] = absurl
            modifiedTime = response.selector.xpath('//div[@class="download"]//tr[4]/td[2]/text()').extract().pop()
            try:
                array = time.strptime(modifiedTime, u"%Y/%m/%d")
                item["publishTime"] = time.strftime("%Y-%m-%d", array)
            except Exception, e:
                print e

            des = response.selector.xpath('//div[@class="download"]//tr[6]/td[2]//text()').extract()  #the last "//" aim to locate the different path
            item["description"]  = str().join(des)
            softname = response.selector.xpath('//div[@class="download"]//tr[1]/td[2]/text()').extract().pop()
            #version
            c = re.search(r'[V|v][0-9]+.[0-9]', softname)  # c maybe not exist
            if c :
                c = c.group()
                if c[-2] == "_":  # TL-WR700N_V1_V2_130415.rar    scrapy V2_1 use V2
                    cc = c.split("_")
                    item['productVersion'] = cc[0]
                else:
                    item['productVersion'] = c
            else:
                item['productVersion'] = ""

            #model
            m = softname.split(" ") #TL-TR862 V1.0_TL-TR861 5200L V1.0_130815标准版
            item['productModel'] = m[0].split("_", 1)[0]
            if item['productModel'] == u"企业级路由器应用数据库文件V1.1.9":
                item['productModel'] = ""

            #classify
            pattern = re.compile(r"T(L|D)-..")
            classraw = pattern.match(item['productModel'])
            if classraw:
                category = classraw.group()
                if category in TplinkSpider.router:
                    item["productClass"] = "Router"
                elif category in TplinkSpider.switch:
                    item["productClass"] = "Switch"
                elif category in TplinkSpider.camera:
                    item["productClass"] = "Camera"
                elif category in TplinkSpider.modem:
                    item["productClass"] = "Modem"
                elif category in TplinkSpider.ap:
                    item["productClass"] = "Ap"
                elif category in TplinkSpider.printing_server:
                    item["productClass"] = "Printing_server"
                else:
                    item["productClass"] = ""

            else:
                if item['productModel'] in TplinkSpider.NetworkTVBox:
                    item["productClass"] = "NetworkTVBox"
                elif item['productModel'] == "TG1":
                    item["productClass"] = "Router"
                else:
                    item["productClass"] = ""
            yield item
            print "firmware name:",item["firmwareName"]
        return











