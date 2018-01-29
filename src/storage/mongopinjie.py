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


MONGO_URI="127.0.0.1"
MONGO_PORT=27017
MONGO_DATABASE="firmwareAnalytics"
MONGO_COLLECTION="crawlfirm170504"

conn = pymongo.MongoClient(MONGO_URI)
db = conn.get_database(MONGO_DATABASE )
collection = db.get_collection(MONGO_COLLECTION)


def download(cur):
    url = cur['url']  # 把link赋值给mylink
    manufacturer = cur['manufacturer']  # 把firm赋值给firmname
    print url
    #urlheadtomato = "http://tomato.groov.pl"
    #urlheadubiquiti = "http://www.ubnt.com"


    '''
    collection.update({'_id': cur['_id']}, {
        "$set": {
            'url':urlheadtomato + url
            }})
    return
    '''
#manufact = "tomato"
manufact = "ubiquiti"



def multiprocess():
    pool = multiprocessing.Pool(processes=2)

    try:
        print db
        print collection
        if collection.find({'manufacturer':manufact}).count() > 0:
            flist = list(collection.find({"manufacturer":manufact}))
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





