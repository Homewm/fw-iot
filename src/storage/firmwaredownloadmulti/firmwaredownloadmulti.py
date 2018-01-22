#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="zhaoweiwei"
__time__="2018.01.22"

import multiprocessing
import pymongo
import os
import time
import urllib2
import urllib

#get mongodb info
import codecs
import ConfigParser
config = ConfigParser.ConfigParser()
configfile = r'./scrapy.cfg'
config.readfp(codecs.open(configfile,'r','utf-8'))
MONGO_URI = config.get('mongo_cfg',"MONGO_IP")
MONGO_PORT = config.get('mongo_cfg',"MONGO_PORT")
MONGO_DATABASE = config.get('mongo_cfg',"MONGO_DATABASE")
MONGO_COLLECTION = config.get('mongo_cfg',"MONGO_SCRAPY_COLLECTION_NAME")
dirs_root = config.get('other_cfg',"DOWNLOAD_DIR")

file_size = 104857600  # 默认文件大小是100m
file_size = int(file_size)


conn = pymongo.MongoClient(MONGO_URI,int(MONGO_PORT),maxPoolSize=None)
db = conn.get_database(MONGO_DATABASE )
collection = db.get_collection(MONGO_COLLECTION)


# 加header，模拟浏览器
header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}

def download(cur):
    name = cur['firmwareName']  # 把文件名赋值给name
    url = cur['url']  # 把link赋值给mylink
    manufacturer = cur['manufacturer']  # 把firm赋值给firmname


    dirs = os.path.join(dirs_root, manufacturer)  # 在FIRMWARE下根据厂商名建立新文件夹
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    filename = os.path.join(dirs, name)  # 定义文件的绝对路径
    timeModel = '%Y-%m-%d'

    # 判断文件是否已经存在，若不存在，继续下载，若存在，输出路径不下载
    if os.path.exists(filename):
        if os.path.getsize(filename) > 1:
            print filename, '已经存在'  # 已经下载过的文件，修改status值

            collection.update({'_id': cur['_id']}, {
                "$set": {
                    'status': 1,
                    'firmwareSize': os.path.getsize(filename),  # 取大小
                    'downloadTime': time.strftime(timeModel, time.localtime())}})
            return


    trytime = 3
    while trytime > 0:
        try:
            res = urllib2.urlopen(urllib2.Request(url, None, header), timeout=20)  # 15

            try:
                fsize = res.headers["content-length"]
                print fsize
                fsize = int(fsize)
                if fsize < file_size:
                    urllib.urlretrieve(url, filename)
                    #with open(filename, 'wb') as f:
                    #    f.write(res.read())
                    #    f.close()

                    collection.update({'_id': cur['_id']}, {
                        "$set": {
                            'status': 1,
                            'firmwareSize': os.path.getsize(filename),  # 取大小
                            'downloadTime': time.strftime(timeModel, time.localtime())}})  # 取时间
                    print"第一次修改成功"
                else:
                    #status 3 for big file
                    collection.update({'_id': cur['_id']}, {
                        "$set": {
                            'status': 3}})
                break
            except Exception, e:
                print e
        except Exception, e:
            print e
            trytime -= 1
    else:
        #status download failed for net or other
        collection.update(
            {"_id": cur['_id']}, {"$set": {'status': 4}})
        return




def multiprocess():
    pool = multiprocessing.Pool(processes=25)

    try:
        print db
        print collection
        if collection.find({'status':0}).count() > 0:
            flist = list(collection.find({"status":0}))
            for url in flist:
                pool.apply_async(download, (url, ))
            pool.close()
            pool.join()
            print "sub-process status 0 done"
        else:
            return 0
    except Exception, e:
        print e


if __name__ == "__main__":
    multiprocess()





