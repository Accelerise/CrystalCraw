import pymongo
import json


class DB(object):
    def __init__(self,ip,port):
        self._conn = None
        self._ip = ip
        self._port = port
        self._db = None
        self._id = 0


    def createDB(self,db):
        self._conn = pymongo.MongoClient(host=self._ip, port=self._port)
        self._db = self._conn[db]


    def insertDB(self,table,dict):
        for colName in dict:
            print colName
            self._id = self._id + 1
            self._db[table].insert({'id' : self._id,colName : dict[colName]})


    def insertDBforOne(self,table,document):
        self._db[table].insert(document)


    def searchDataByRange(self,table,start,end):
        resData = self._db[table].find({"id": {"$gte": start, "$lte": end}},{"_id":0})
        return resData

    def searchData(self,table):
        resData = self._db[table].find()
        return resData


    def createId(self):
        self._db["ids"].save({"name": "user", "id": 0})


    def incId(self):
        row = self._db["ids"].find_and_modify(update = {"$inc":{'id':1}}, query = {"name":"user"}, new = True)
        return row['id']


    def searchId(self):
        row = self._db["ids"].find({"name":"user"})
        return row[0]['id']