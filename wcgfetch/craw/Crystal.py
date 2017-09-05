#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import threading
import time

from lxml import etree
from Bloom import BloomFilter
from Tool import Queue,File
from Xpath import Xpath
from Rules import Rules
import requests
from Downloader import Downloader
from Parser import Parser
from Configer import Configer
from LogUtil import LogUtil
from Model import WCG
import random


class Crystal:
    # 构造函数
    def __init__(self,projectName,taskId):
        self._projectName = projectName
        self._taskId = taskId
        self._xpath = None
        self._rules = None
        self._parser = None
        self._downloader = None
        self._config = None
        self._bf = None
        self._queue = None
        self._hostInfo = None
        self._lock = threading.Lock()
        self.initComponents()

    # void 初始化各组件
    def initComponents(self):
        self.initConfig()
        self.initXpath()
        self.initRules()
        self.initBF()
        self.initQueue()
        self.initParser()
        self.createDir(self._projectName)

    # void 运行
    def run(self,flag):
        #self.threadAdd()
        LogUtil.start_log()
        #empty_count = 0
        _downloader = self.newDownloader()

        while True:
            if not self._queue.empty():
                pagelink = self._queue.pop()

                host = self._hostInfo["host"]
                LogUtil.n("开始下载页面："+pagelink,self._taskId)
                try:
                    page = _downloader.get(pagelink)
                except Exception:
                    continue
                LogUtil.n("下载页面完成："+pagelink,self._taskId)
                pagelink = pagelink.encode("UTF-8")
                if flag=="work":
                    self._parser.process_item(host=host,pagelink=pagelink,page=page)
                elif flag=="master":
                    self._parser.initCollectURLs(host=host, pagelink=pagelink, page=page)
            else:
                # if empty_count < 3:
                #     empty_count = empty_count + 1
                #     time.sleep(3)
                # else:
                #     break
                break
            ran = 0.5 - random.random()
            time.sleep(self._config["DOWNLOAD_DELAY"] * (1 + ran))

        #self.threadReduce()
        LogUtil.end_log()


    # void 初始化起始URL
    def initStartUrl(self, targetUrl):
        self.start_url = targetUrl
        self._hostInfo = self.parseUrl(self.start_url[0])
        self._parser.setProto(self._hostInfo["proto"]) # 默认为https://
        self._parser.setDomain(self._hostInfo["fir"])
        for each in self.start_url:
            self._queue.put(each)
            print each
        LogUtil.i("设置URL完成")

    # void 初始化xpath
    def initXpath(self):
        # 获取name->xpath字典
        self._xpath = Xpath()
        if(not self._xpath.isManual()):
            dic = self.getXpathFromMGDB()
            self._xpath.initXpath(dic)
        LogUtil.i("初始化Xpath完成")

    # void 初始化rules
    def initRules(self):
        # 获取url规则数组
        self._rules = Rules()
        if(not self._rules.isManual()):
            arr = self.getRulesFromMGDB()
            detail = self.getDetailUrlFromMGDB()
            if (detail is not None):
                arr.append(detail)
            # 如果能获取到数据，说明用户在web前台填写了url规则
            if arr is not None:
                self._rules.initRules(arr,detail)
        LogUtil.i("初始化Rules完成")

    # void 首先从分布式系统读取配置，然后读取本地配置，本地配置优先
    def initConfig(self):
        self._config = {}

        # 本地配置
        localConfig = Configer.getConfig()
        for row in localConfig:
            self._config[row] = localConfig[row]
        # 分布式配置
        db = WCG()
        resData = db.searchData('config_task' + str(self._taskId)) #读数据库配置
        remoteConfig = {}
        for res in resData:
            for key in res:
                remoteConfig[key] = res[key]
        for row in remoteConfig:
            self._config[row] = remoteConfig[row]

    # void 初始化downloader
    def newDownloader(self):
        downloader = Downloader()
        CHROME_ENABLE = self._config["CHROME_ENABLE"]
        downloader.setChromeEnable(CHROME_ENABLE)
        LogUtil.i("初始化Downloader完成")
        return downloader

    # void 初始化过滤器
    # - int -   number(可选) 过滤器最大过滤数
    # - float - errorRate(可选) 过滤器允许的哈希冲突率
    def initBF(self,number = 1000000,errorRate=0.0001):
        # if 配置文件中配置了过滤器的数目和错误率:
        # number =
        # errorRate =
        self._bf = BloomFilter(host=self._config['REDIS_IP'],db=self._taskId,key="bloomfilter_task" + str(self._taskId))
        LogUtil.i("初始化Filter完成")

    # void 初始化URL队列
    def initQueue(self):
        self._queue = Queue()
        LogUtil.i("初始化Queue完成")

    # void 初始化Parser
    def initParser(self):
        self._parser = Parser(self)
        LogUtil.i("初始化Parser完成")

    # {} / False 解析URL
    # 成功则返回一个字典 内含{"all":协议+host,"fir":一级域名,"sec":二级域名,"proto":协议,"host":host}
    # 失败则返回 False
    # - String - url 待解析链接
    def parseUrl(self,url):
        reobj = re.compile(r"""(?xi)\A
        ([a-z][a-z0-9+\-.]*://)
        (([a-z0-9\-_~%]+)\.)?
        (([a-z0-9\-_~%]+)\.)?
        ([a-z0-9\-._~%]+)
        """)
        match = reobj.search(url)
        res = {}
        if match:
            if match.group(5) is None:
                res["sec"] = None
                res["fir"] = match.group(3)
            else:
                res["sec"] = match.group(3)
                res["fir"] = match.group(5)
            res["all"] = match.group(0)
            res["proto"] = match.group(1)
            res["top"] = match.group(6)
            res["host"] = res["all"][len(res["proto"]):]
            return res
        else:
            return False

    # void 创建工作目录
    # - String - projectName 工程名
    def createDir(self,projectName):
        self.fileTool = File()
        self.fileTool.setDir(projectName)
        LogUtil.i("创建工作目录")

    def threadAdd(self):
        self._lock.acquire()
        self._threadCount = self._threadCount + 1
        self._lock.release()

    def threadReduce(self):
        self._lock.acquire()
        self._threadCount = self._threadCount - 1
        self._lock.release()

    def getThreadCount(self):
        self._lock.acquire()
        res = self._threadCount
        self._lock.release()
        return res

    def getXpathFromMGDB(self):
        db = WCG()
        resData = db.searchDataByRange('task', self._taskId, self._taskId)
        dict = {}
        for res in resData:
            for key in res['attr']:
                dict[key['name']] = key['value']
        LogUtil.i("从数据库获取给定的xpath规则")
        return dict
        pass

    # void 从数据库获取给定的url规则
    def getRulesFromMGDB(self):
        db = WCG()
        resData = db.searchDataByRange('task', self._taskId, self._taskId)
        dict = []
        flag = False
        for res in resData:
            for key in res:
                if(key == "dataUrl"):
                    flag = True
                    break
        if flag:
            for res in resData:
                for key in res['dataUrl']:
                    dict.append(key)
            LogUtil.i("从数据库获取给定的url规则")
            return dict
        else:
            return None

    def getDetailUrlFromMGDB(self):
        db = WCG()
        resData = db.searchDataByRange('task', self._taskId, self._taskId)
        flag = False
        for res in resData:
            for key in res:
                if(key == "detailUrl"):
                    flag = True
                    dict = res['detailUrl']
                    break
        if flag:
            return dict
        else:
            return None

    def start(self,flag,targetUrl):
        self.initStartUrl(targetUrl)
        self._threadCount = 0
        print "开启线程数 "+str(self._config["TREADING_COUNT"])
        if flag=="work":
            poo = []
            for i in range(self._config["TREADING_COUNT"]):
                poo.append(threading.Thread(target=self.run,args=("work",)))
            for task in poo:
                task.start()
            for task in poo:
                task.join()

        elif flag=="master":
            self.run("master")

    def start_single(self,flag,targetUrl):
        self.initStartUrl(targetUrl)
        if flag == "work":
            self.run("work")
        elif flag == "master":
            self.run("master")

