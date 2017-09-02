#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import threading
import time
import signal

from lxml import etree
from Bloom import Bloomfilter
from Tool import Queue,File
from Xpath import Xpath
from Rules import Rules
import requests
from Downloader import Downloader
from Parser import Parser
from Configer import Configer
from LogUtil import LogUtil
from httplib import BadStatusLine

class Crystal:
	# 构造函数
	def __init__(self,projectName):
		self._projectName = projectName
		self._xpath = None
		self._rules = None
		self._parser = None
		self._config = None
		self._bf = None
		self._queue = None
		self._hostInfo = None
		self._lock = threading.Lock()

		self.initComponents()

		self.firstState()

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
	def run(self):
		self.threadAdd()
		LogUtil.start_log()
		empty_count = 0
		_downloader = self.newDownloader()
		while self.getState() == "running":
			self._lock.acquire()
			if not self._queue.empty():
				pagelink = self._queue.pop()
				self._lock.release()

				# parseRes = self.parseUrl(pagelink)
				# if parseRes is None:
				# 	host = None
				# 	# 该url不合法
				# else:
				host = self._hostInfo["host"]
				try:
					page = _downloader.get(pagelink)
				except Exception:
					continue
				self._parser.process_item(host=host,pagelink=pagelink,page=page)
				
			else:
				self._lock.release()
				if empty_count < 3:
					empty_count = empty_count + 1
					time.sleep(5)
				else:
					break
			time.sleep(self._config["DOWNLOAD_DELAY"])

		self.threadReduce()
		LogUtil.end_log()


	# void 初始化起始URL
	def initStartUrl(self):
		# 修改这里获取起始URL的途径

		if self.getState() == "restart":
			self.start_url = self.loadQueue()
		else:
			self.start_url = ["https://s.taobao.com/search?q=%E6%AF%9B%E8%A1%A3%E7%94%B7"]

		self._hostInfo = self.parseUrl(self.start_url[0])
		self._parser.setProto(self._hostInfo["proto"]) # 默认为https://
		self._parser.setDomain(self._hostInfo["fir"])
		for each in self.start_url:
			self._queue.put(each)
		LogUtil.i("初始化起始URL完成")

	# void 初始化xpath
	def initXpath(self):
		# 获取name->xpath字典
		self._xpath = Xpath()
		if(not self._xpath.isManual()):
			dic = self.getXpathFromMGDB()
			self._xpath.initXpath(dic)
		LogUtil.i("初始化Xpath完成")

	# void 初始化rules
	def initRules(self,detailUrl = None):
		# 获取url规则数组
		self._rules = Rules()
		if(not self._rules.isManual()):
			arr = self.getRulesFromMGDB()
			# 如果能获取到数据，说明用户在web前台填写了url规则
			if arr is not None:
				self._rules.initRules(arr,detailUrl)
		LogUtil.i("初始化Rules完成")

	# void 读取本地配置
	def initConfig(self):
		self._config = {}

		# 本地配置
		localConfig = Configer.getConfig()
		for row in localConfig:
			self._config[row] = localConfig[row]

	# void 初始化downloader
	def newDownloader(self):
		downloader = Downloader()
		downloader.setChromeEnable(True)
		LogUtil.i("初始化Downloader完成")
		return downloader

	# void 初始化过滤器
	# - int -   number(可选) 过滤器最大过滤数
	# - float - errorRate(可选) 过滤器允许的哈希冲突率
	def initBF(self,number = 1000000,errorRate=0.0001):
		# if 配置文件中配置了过滤器的数目和错误率:
		# number = 
		# errorRate =
		self._bf = Bloomfilter(number,errorRate)
		LogUtil.i("初始化Filter完成")

	# void 初始化URL队列
	def initQueue(self):
		self._queue = Queue()
		LogUtil.i("初始化Queue完成")

	# void 初始化Parser
	def initParser(self):
		self._parser = Parser.getInstance(self)
		
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

	def setState(self,state):
		self._state = state
		# init running stop restart end

	def getState(self):
		return self._state

	def firstState(self):
		if self.fileTool.fileExist("queue") :
			self.setState("restart")
		else:
			self.setState("init")
	
	# void 创建工作目录
	# - String - projectName 工程名
	def createDir(self,projectName):
		self.fileTool = File()
		self.fileTool.setDir(projectName)
		LogUtil.i("创建工作目录")


	def saveQueue(self):
		if self.fileTool.fileExist("queue") :
			self.fileTool.fileRemove("queue")
		while not self._queue.empty():
			url = self._queue.pop()
			self.fileTool.fileAppend("queue",url + "\n")

	def loadQueue(self):
		return self.fileTool.fileReadLine("queue")
	
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


	# void 从数据库获取给定的xpath规则
	def getXpathFromMGDB(self):
		dic = {}

		dic["名称"] = '//*[@id="J_Title"]/h3/text()'
		dic["价格"] = '#J_StrPrice > em.tb-rmb-num' 
		dic["图片地址"] = '//*[@id="J_ShopInfo"]/a/img/@src'
		LogUtil.i("从数据库获取给定的xpath规则")
		return dic


	# void 从数据库获取给定的url规则
	def getRulesFromMGDB(self):
		LogUtil.i("从数据库获取给定的url规则")
		return ["https://s.taobao.com/search\?.*q=%E6%AF%9B%E8%A1%A3%E7%94%B7.*","https://item.taobao.com/item.htm\?id=\d+.*"]

	def start(self):
		self.initStartUrl()
		self.setState("running")
		self._threadCount = 0
		print "开启线程数 "+str(self._config["TREADING_COUNT"])
		poo = []
		for i in range(self._config["TREADING_COUNT"]):
			poo.append(threading.Thread(target=self.run))
		for task in poo:
			task.setDaemon('True')
			task.start()
		try:
			while self.getThreadCount() != 0:
				time.sleep(2)
		except KeyboardInterrupt as e:
			self.setState("stop")
			for task in poo:
				task.join()
			LogUtil.d('正在停止本次爬取，之后您再次开启时可接着上一次继续爬取')

		if self.getState() == "stop":
			self.saveQueue()
			self.setState("end")
		elif self.getState() == "running":
			self.setState("end")

	
if __name__ == '__main__':

	project = Crystal("淘宝毛衣男")
	project.start()
	# project.initStartUrl()
	# project.saveQueue()
	# project.loadQueue()