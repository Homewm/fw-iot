from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse
import FirmCrawler.items as MI
from sets import Set
import time
import re
import urllib2

import urlparse


class BelkinSpider(Spider):
    name = "belkin"
    allowed_domains = ["belkin.com", "belkin.force.com"]
    start_urls = ["http://www.belkin.com/us/support"]
    suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip", "ipk",
              "bz2", "BIN", "gz", "7z", "lzma", "tgz", "exe", "ZIP", "tar", "ubi",
              "uimage", "rtf", "ram", "elf", "ipa", "chm", "dsw", "dsp", "clw", "mav",
              "dav", "upg","bfp","hex"]
    allsuffix = Set()
    timeout = 10

    def parse(self, response):
        if not response.xpath(
                "//form[@id='productSearchForm']//input[@name='category']/@value").extract()[0]:
            for category in response.xpath("//form[@id='productSearchForm']/div[1]//ul[@class='select-options']//a/@data-id").extract():
                yield FormRequest.from_response(response,
                                                formname="productSearchForm",
                                                formdata={
                                                    "category": category},
                                                callback=self.parse)
        elif not response.xpath("//form[@id='productSearchForm']//input[@name='subCategory']/@value").extract()[0]:
            for subcategory in response.xpath("//form[@id='productSearchForm']/div[2]//ul[@class='select-options']//a/@data-id").extract():
                yield FormRequest.from_response(response,
                                                formname="productSearchForm",
                                                formdata={
                                                    "subCategory": subcategory},
                                                callback=self.parse)
        else:
            for product in response.xpath("//form[@id='productSearchForm']/div[3]//ul[@class='select-options']//a/@data-id").extract():
                yield Request(
                    url=urlparse.urljoin(
                        response.url, "/us/support-product?pid=%s" % (product)),
                    headers={"Referer": response.url},
                    callback=self.parse_product)

    def parse_product(self, response): #enter the url like:http://www.belkin.com/us/support-product?pid=01t80000002K3KkAAK
        print "parse_product"
        for item in response.xpath("//div[@id='main-content']//a"):
            if "firmware" in item.xpath(".//text()").extract()[0].lower():
                yield Request(
                    url=urlparse.urljoin(
                        response.url, item.xpath(".//@href").extract()[0]),
                    headers={"Referer": response.url},
                    meta={"product": response.xpath("//p[@class='product-part-number']/text()").extract()[0].split(' ')[-1]},
                    callback=self.parse_download)

    def parse_download(self, response):  #nested frame
        iframe = ""
        try:
            iframe = response.xpath("//div[@id='main-content']/iframe/@src").extract()
        except:
            pass


        if iframe:
            yield Request(
                url=iframe[0],
                headers={"Referer": response.url},
                meta={"product": response.meta["product"]},
                callback=self.parse_redirect)

    def parse_redirect(self, response):
        #print "qiantaokuangjai:",response.url
        for text in response.body.split('\''):
            if "articles/" in text.lower() and "download/" in text.lower():
                yield Request(
                    url=urlparse.urljoin(response.url, text),
                    headers={"Referer": response.url},
                    meta={"product": response.meta["product"]},
                    callback=self.parse_kb)

    def parse_kb(self, response):
        #print "parse kb:",response.url
        desc = response.xpath('//div[@id="articleContainer"]/h1/text()').extract()[0]

        # initial html tokenization to find regions segmented by e.g. "======"
        # or "------"
        filtered = response.xpath(
            "//div[@class='sfdc_richtext']").extract()[0].split("=-")

        for entry in [x and x.strip() for x in filtered]:
            resp = HtmlResponse(url=response.url, body=entry,
                                encoding=response.encoding)

            for link in resp.xpath("//a"):
                href = link.xpath("@href").extract()[0]


                if "cache-www" in href:  #http://cache-www.belkin.com/support/dl/belkin_switch_package_cirque_master_20090827.bfp
                    filename = href.rsplit('/', 1)[-1]
                    filetype = filename.split('.')[-1]
                    BelkinSpider.allsuffix.add(filetype)

                    if filetype in BelkinSpider.suffix:

                        item = MI.FirmcrawlerItem()
                        item["manufacturer"] = "belkin"
                        item["crawlerTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        item["url"] = href
                        item["firmwareName"] = filename
                        print "firmware name:",item["firmwareName"]
                        item["description"] = desc

                        text = resp.xpath("//text()").extract() #get all text of all page
                        #version
                        version = ""
                        match = re.search(r"((?:[0-9])(?:[\w-]*\.[\w-]*)+)",
                                          " ".join(text).replace(u"\xa0", " ").strip())
                        if match:
                            version = match.group()
                        item["productVersion"] = version

                        #publishtime
                        # invoking the network
                        item["publishTime"] = ""
                        res = ""
                        try:
                            res = urllib2.urlopen(urllib2.Request(
                                item["url"], None), timeout=BelkinSpider.timeout)
                        except Exception, e:
                            print e
                        modfile = res.headers["last-modified"]
                        try:
                            array = time.strptime(modfile, u"%a, %d %b %Y %H:%M:%S GMT")
                            item["publishTime"] = time.strftime("%Y-%m-%d", array)
                        except Exception, e:
                            print e

                        item["productClass"] = ""
                        item["productModel"] = ""

                        print "firmware name::", item["firmwareName"]
                        yield item
        #print "allsuffix:",BelkinSpider.allsuffix
        return













