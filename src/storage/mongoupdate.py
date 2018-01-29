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
import linecache


MONGO_URI="127.0.0.1"
MONGO_PORT=27017
MONGO_DATABASE="firmwareAnalytics"
MONGO_COLLECTION="crawlfirm170504"

conn = pymongo.MongoClient(MONGO_URI)
db = conn.get_database(MONGO_DATABASE )
collection = db.get_collection(MONGO_COLLECTION)

firmwareResultDir = "/disk8Tosd4/osd4/downloadNewFirmwareNotDel/FirmwareNewResult"


def changeMongo(cur):
    manufacturer = cur['manufacturer']  # 把firm赋值给firmname
    firmwareName = cur['firmwareName']
    extractDir = '_' + firmwareName + ".extracted"
    extractFailed = '_' + firmwareName + "_failed"
    extractAbstract = '_' + firmwareName + "_abstract"
    extractTargz = '_' + firmwareName + ".tar.gz"
    extractTree = '_' + firmwareName + "_tree.json"
    extractDirpath = firmwareResultDir + '/' + manufacturer + '/' + extractDir
    extractFailedpath = firmwareResultDir + '/' + manufacturer + '/' + extractFailed
    extractAbstractpath = firmwareResultDir + '/' + manufacturer + '/' + extractAbstract
    if os.path.exists(extractFailedpath):
        unZipStatus = "False"
        collection.update({'_id':cur['_id']},{
            "$set":{
                'unZipStatus':unZipStatus
            }
        })

    elif os.path.exists(extractDirpath):
        tarSize = linecache.getline(extractAbstractpath,5).replace('\n',"").rsplit(':',1)[-1]
        isa = linecache.getline(extractAbstractpath,3).replace('\n',"").rsplit(':',1)[-1]
        md5 = linecache.getline(extractAbstractpath,2).replace('\n',"").rsplit(':',1)[-1]
        firmwareDir = manufacturer + '/' + extractDir
        tarPath = manufacturer + '/' + extractTargz
        treePath = manufacturer + '/' + extractTree
        #txtpath ,abstract文本相对路径
        txtPath = manufacturer + '/' + extractAbstract 
        #pdfPath = manufacturer + '/' +
        unZipStatus = "True"
        
        collection.update({'_id':cur['_id']},{
            "$set":{
                'tarSize':tarSize,
                'isa':isa,
                'md5':md5,
                'firmwareDir':firmwareDir,
                'tarPath':tarPath,
                'treePath':treePath,
                'txtPath':txtPath,
                'unZipStatus':unZipStatus
            }
        })
        


    '''
    collection.update({'_id': cur['_id']}, {
        "$set": {
            'url':urlheadtomato + url
            }})
    return
    '''




def multiprocess():
    pool = multiprocessing.Pool(processes=1)

    try:
        print db
        print collection
        if collection.find({"status":1}).count() > 0:
            flist = list(collection.find({"status":1}))
            for url in flist:
                #print url
                pool.apply_async(changeMongo, (url, ))
            pool.close()
            pool.join()
            print "sub-process status 0 done"
        else:
            return 0
    except Exception, e:
        print e


if __name__ == "__main__":
    multiprocess()





