# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pymongo
import json


class WCG(object):
    def __init__(self):
        ip = '172.31.191.252'
        port = 27017
        dbName = 'wcgfetch'
        self._conn = pymongo.MongoClient(host = ip, port = port)
        self._db = self._conn[dbName]

    def createId(self, collection):
        if (self.searchId(collection) == -1):
            self._db["ids"].save({"name": collection, "id": 0})
        else:
            self.motify("ids", {"name": collection}, {"id": 0})

    def createCollection(self,collection):
        if (collection in self._db.collection_names()):
            coll = self._db[collection]
            coll.drop()
        self._db.create_collection(collection)

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
        resData = self._db[collection].find(projection={'_id': False})
        return resData

    def searchKeyById(self, collection, key, id):
        resData = self._db[collection].find({"id": id},{"_id":0})
        return resData[0][key]

    def searchDataByStatus(self,collection , status):
        resData = self._db[collection].find({"status": status}, projection={'_id': False})
        return resData

    def insertDBforOne(self,collection,document):
        self._db[collection].insert(document)

    def motify(self,collection,need,document):
        self._db[collection].update(need, {"$set": document})




