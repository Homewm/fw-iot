# -*- coding: UTF-8 -*-

from sets import Set
from scrapy.spiders import Spider
import scrapy
import urllib2
import urlparse
import FirmCrawler.items as MI
import re
import time
from lxml import etree

header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}
a = "http://www.linksys.com/us/"

class OpenwrtSpider(Spider):
    name = "cisco"
    timeout = 8
    trytimes = 3
    start_urls = [
       'http://www.linksys.com/us/search?text=firmware&type=support_downloads'
    ]
    # must be lower character
    #suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip"]
    ahref = []
    #allsuffix = Set()


    def parse(self, response):
        try:
            #print response
            ahref = response.xpath('//ul[@class="support-list"]/li/a/@href').extract()
           # print ahref
            index = 0
            for x in ahref:
                index+=1
               # print "==================",index,"============="

                x = urlparse.urljoin(a,x) #拼接url
                t = 4
                while t > 0:
                    try:
                        res = urllib2.urlopen(urllib2.Request(x,None,header),timeout=10)
                        html = res.read()
                        html = etree.HTML(html)
                        zzs = html.xpath('//div[@id="support-article-downloads"]')
                        if not zzs:
                            t=0
                            continue

                        for x in zzs:
                            z1 = x.xpath('.//a[@target="_blank"]')
                            for y in z1:
                                zz2 = None
                                try:
                                    zz1 = y.xpath('./text()')[0]
                                    zz2 = y.xpath('./@href')[0]
                                   # print zz2
                                except:
                                    pass
                                if zz1 == 'Download':

                                        link = zz2
                                        name = link.split("/")[-1]
                                        name1 = name.replace('.' + name.split('.')[-1],"")
                                        item = MI.FirmcrawlerItem()

                                        item["publishTime"]=""
                                        item["productVersion"] = ""
                                        item["productModel"]=""
                                        item["description"]= ""
                                        item["firmwareName"] = name
                                        item["manufacturer"] = "Cisco"

                                        a1 = re.compile(r'[V,v]*[1-9]\.[0-9]+((\.[0-9]+)*)+(\.[0-9]+)*')
                                        a2 = a1.search(name1)
                                        if a2:
                                            item["productVersion"] = a2.group()
                                            #print item["productVersion"]

                                        try:
                                            x1 = name1.split("_")[0]
                                            x2 = name1.split("_")[1]
                                            mat2Ver=a1.search(x2)
                                            if mat2Ver!=None:
                                                if x1=="FW":
                                                    item["productModel"] = x2.replace(item["productVersion"],"").replace("-","")
                                                else:
                                                    item["productModel"] =x1.split("v")[0].split("V")[0]
                                            #剔除一些固件
                                            if x1 in ["wap54g","wet11","win10","win81","win8"]:
                                                item["productModel"] = ""

                                            if x1 in ["FW","MBs","SW","SetupWizardMac","CameraSetupCD","MIBs"]:
                                                if name1.split("_")[1]=="WVC80N":
                                                    item["productModel"] = name1.split("_")[1]
                                                else:
                                                    if mat2Ver!=None:#匹配FW_EA6900-1.1.42.161129_prod.img
                                                        item["productModel"] = x2.replace(item["productVersion"],"").replace("-", "")
                                                    else:
                                                        item["productModel"] = name1.split("_")[1].split("v")[0].split("V")[0]
                                                if item["productModel"] == "Linksys":
                                                    item["productModel"] = ""
                                            if x1 == "Setup":
                                                item["productModel"] = ""
                                            if x2 in ["MIB","Vista","Win7","XP","Mac","Win","CD","USCAN","Utility"]:
                                                if name1.split("_")[0] == "WVC80N":
                                                    item["productModel"] = name1.split("_")[0]
                                                else:
                                                    item["productModel"] = name1.split("_")[0].split("v")[0].split("V")[0]
                                        except:
                                            pass

                                        try:

                                            name2 = name1.split(".")[0]
                                            name21 = name2.split("v")[0].split("V")[0]
                                            if name2 in ["LinksysConnect", "Setup", "ExtenderSetups", "CiscoConnect",
                                                         "ExtenderSetup"]:
                                                item["productModel"] = name1.split(".")[1]

                                            elif name2 == "Downloadable":
                                                item["productModel"] = name1.split(".")[2]
                                            elif name21 in ["EA2700", "EA3500", "PLW", "E4200", "EA4500"]:
                                                item["productModel"] = name21
                                        except:
                                            pass

                                        try:
                                            # 针对这种情况分类LGS300-boot-1005.rfb
                                            name3 = name1.split("-")[1]
                                            if name3 in ["boot", "11021", "510", "11027", "EU", "setupWizard",
                                                         "setupWizard_0", "Mac", "Windows"]:
                                                item["productModel"] = name1.split("-")[0]
                                        except:pass

                                        reg = re.compile(r'20[0-1][0-9][0-1][0-9][0-3][0-9]')
                                        regs = reg.search(item["firmwareName"])
                                       # print regs
                                        if regs != None:
                                            item["publishTime"] = regs.group()

                                        item["url"] = link
                                        Ap_bridge = ["RE", "WES", "WUMC", "LAPAC", "LAPN",
                                                     "WAP"]  # AP  , RP repeater  ,net bridge
                                        Modem = ["PLE", "PLW", "PLS", "WAG"]
                                        Net_adapter = ["AE", "WUSB"]  # network adapter
                                        Camera = ["WVC"]
                                        Switch = ["LGS"]
                                        Router = ["E10", "E12", "E15", "E17", "E21", "E25", "E30", "E32", "E42", "E800",
                                                  "E83",
                                                  "E84", "E90", "EA", "WRT", "LRT", "M10", "M20", "X10", "X20", "X35",
                                                  "X62"]
                                        alls = [Ap_bridge, Modem, Net_adapter, Camera, Switch, Router]
                                        aa = item["productModel"]
                                        for x in alls:
                                            for y in x:
                                                if y in aa:
                                                    if x == Ap_bridge:
                                                        item["productClass"] = "Ap_bridge"
                                                    elif x == Modem:
                                                        item["productClass"] = "Modem"
                                                    elif x == Net_adapter:
                                                        item["productClass"] = "Net_adapter"
                                                    elif x == Switch:
                                                        item["productClass"] = "Switch"
                                                    elif x == Router:
                                                        item["productClass"] = "Router"
                                                    else:
                                                        item["productClass"] = ""
                                        print "firmware name:",item["firmwareName"]
                                        yield item
                                       # print item
                        t = 0
                    except Exception,e:
                        print e
                        t -= 1
        except Exception,e:
            print e






