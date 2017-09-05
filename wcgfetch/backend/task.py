# -*- coding: utf-8 -*-
from models import WCG
from craw.Crystal import Crystal
from myapp.agent import spider
import time
import datetime


def utc2local(utc_st):
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

class Task(object):
    def __init__(self,id):
        self.id = id
        self.method = None
        self.mainUrl = None
        self.detailUrl = None
        self.dataUrl = None
        self.attr = None
        self.time = None
        self.status = None
        self.workNum = "1"
        name = "craw_task" + str(self.id)
        self.crystal = Crystal(name , self.id)

    def getTaskFromMGDB(self):
        db = WCG()
        resData = db.searchDataByRange("task", self.id, self.id)
        try:
            for res in resData:
                self.method = res['method']
                self.mainUrl = res['mainUrl']
                self.detailUrl = res['detailUrl']
                self.dataUrl = res['dataUrl']
                self.attr = res['attr']
                self.time = res['time']
                self.status = res['status']
                self.workNum = res['selectWorker']

        except Exception, e:
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message

    def initTask(self):
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        #startTime = time.strftime('%Z', time.localtime())
        db = WCG()
        db.motify("task", {"id": self.id}, {"startTime": startTime})
        self.crystal.start_single("master",[self.mainUrl])

    def startTask(self):
        db = WCG()
        collection = "url_task" + str(self.id)
        cur = 0
        end = db.searchId(collection)
        while cur < end:
            end = db.searchId(collection)
            status = db.searchKeyById("task", "status", self.id)
            self.workNum = db.searchKeyById("task", "selectWorker", self.id)
            flag = False
            if (status == "success"):
                flag = True
            if (flag):
                break
            if (cur + 50 <= end):
                resData = db.searchDataByRange(collection, cur, cur + 50)
                cur = cur + 50
                print "当前链接数"+str(cur)
                url = []
                i = 0
                craw = []
                for document in resData:
                    url.append(document['url'])
                    i = i + 1
                    if (i % 10 ==0):
                        if (self.workNum == "1"):
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work3',routing_key='work3')
                            craw.append(tmpcraw)
                        elif (self.workNum == "2"):
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work2',routing_key='work2')
                            craw.append(tmpcraw)
                        else:
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work1',routing_key='work1')
                            craw.append(tmpcraw)
                    url = []
                while True:
                    flag = True
                    for tt in craw:
                        if (tt.ready() != True):
                            flag = False
                    if (flag):
                        break
                    time.sleep(1)

            else:
                resData = db.searchDataByRange(collection, cur, end)
                cur = end
                print "当前链接数" + str(cur)
                url = []
                i = 0
                craw = []
                lenth = resData.count()
                print lenth
                for document in resData:
                    url.append(document['url'])
                    i = i + 1
                    if (i % 10 ==0 or i == lenth):
                        if (self.workNum == "1"):
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work3',routing_key='work3')
                            craw.append(tmpcraw)
                        elif (self.workNum == "2"):
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work2',routing_key='work2')
                            craw.append(tmpcraw)
                        else:
                            tmpcraw = spider.apply_async(args=[self.id,url],queue='work1',routing_key='work1')
                            craw.append(tmpcraw)
                    url = []
                while True:
                    flag = True
                    for tt in craw:
                        if (tt.ready() != True):
                            flag = False
                    if (flag):
                        break
                    time.sleep(1)
        endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db.motify("task", {"id": self.id}, {"endTime": endTime})

    def stopTask(self):
        db = WCG()
        db.motify("task", {"id": self.id}, {"status": "success"})
