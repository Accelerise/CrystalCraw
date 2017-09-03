# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pymongo
import json


class WCG(object):
    def __init__(self):
        ip = '127.0.0.1'
        port = 27017
        dbName = 'wcgfetch'
        self._conn = pymongo.MongoClient(host = ip, port = port, connect= False)
        self._db = self._conn[dbName]

    def createId(self, collection):
        if(self._db["ids"].find({"name": collection}).count() == 0):
            self._db["ids"].save({"name": collection, "id": 0})

    def searchId(self, collection):
        row = self._db["ids"].find({"name":collection})
        if(row.count()>0):
            return row[0]['id']
        else:
            return -1

    def incId(self, collection):
        row = self._db["ids"].find_and_modify(update = {"$inc":{'id':1}}, query = {"name":collection}, new = True)
        return row['id']

    def searchDataByRange(self, collection, start, end):
        resData = self._db[collection].find({"id": {"$gte": start, "$lte": end}},{"_id":0})
        return resData

    def searchData(self, collection):
        resData = self._db[collection].find()
        return resData

    def insertDBforOne(self,collection,document):
        self._db[collection].insert(document)




