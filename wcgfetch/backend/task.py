# -*- coding: utf-8 -*-
from models import WCG
from craw.Crystal import Crystal
from myapp.agent import spider
import time

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
        self.workNum = 1
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
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db = WCG()
        db.motify("task", {"id": self.id}, {"startTime": startTime})
        self.crystal.start("master",[self.mainUrl])

    def startTask(self):
        db = WCG()
        collection = "url_task" + str(self.id)
        cur = 0
        end = db.searchId(collection)
        while cur < end:
            end = db.searchId(collection)
            if (end > 9000000):
                break
            status = db.searchKeyById("task", "status", self.id)
            flag = False
            if (status == "success"):
                flag = True
            if (flag):
                break
            if (cur + 10 <= end):
                resData = db.searchDataByRange(collection, cur, cur + 10)
                cur = cur + 10
                print "当前链接数"+str(cur)
                url = []
                for document in resData:
                    url.append(document['url'])
                if (self.workNum == 1):
                    craw = spider.apply_async(args=[self.id,url],queue='work3',routing_key='work3')
                elif (self.workNum == 2):
                    craw = spider.apply_async(args=[self.id,url],queue='work2',routing_key='work2')
                else:
                    craw = spider.apply_async(args=[self.id,url],queue='work1',routing_key='work1')
                while True:
                    if craw.ready():
                        print('craw:', craw.get())
                        break

            else:
                resData = db.searchDataByRange(collection, cur, end)
                cur = end
                print "当前链接数" + str(cur)
                url = []
                for document in resData:
                    url.append(document['url'])
                if (self.workNum == 1):
                    craw = spider.apply_async(args=[self.id,url],queue='work3',routing_key='work3')
                elif (self.workNum == 2):
                    craw = spider.apply_async(args=[self.id,url],queue='work2',routing_key='work2')
                else:
                    craw = spider.apply_async(args=[self.id,url],queue='work1',routing_key='work1')
                while True:
                    if craw.ready():
                        print('craw:', craw.get())
                        break
                    print('craw:', craw.get())
                    time.sleep(1)
        endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db.motify("task", {"id": self.id}, {"endTime": endTime})

    def stopTask(self):
        db = WCG()
        db.motify("task", {"id": self.id}, {"status": "success"})
