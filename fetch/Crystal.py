#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import threading
import time

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

class Crystal:
	# 构造函数
	def __init__(self,projectName):
		self._projectName = projectName
		self._xpath = None
		self._rules = None
		self._parser = None
		self._downloader = None
		self._configer = None
		self._bf = None
		self._queue = None
		self._hostInfo = None
		self._lock = threading.Lock()

		self.initComponents()

	# void 初始化各组件
	def initComponents(self):
		self._config = Configer.getConfig()
		self.initStartUrl()
		self.initXpath()
		self.initRules()
		
		self.initBF()
		self.initQueue()
		self.initParser()
		self.createDir(self._projectName)
		for each in self.start_url:
			self._queue.put(each)

	# void 运行
	def run(self):
		LogUtil.start_log()
		TIMEOUT_COUNT = 0
		_downloader = self.newDownloader()
		while True:
			self._lock.acquire()
			if not self._queue.empty():
				pagelink = self._queue.pop()
				self._lock.release()

				parseRes = self.parseUrl(pagelink)
				if parseRes is None:
					host = None
					# 该url不合法
				else:
					host = parseRes["host"]
				page = _downloader.get(pagelink)
				self._parser.process_item(host=host,pagelink=pagelink,page=page)
			else:
				self._lock.release()
				if TIMEOUT_COUNT < 3:
					TIMEOUT_COUNT = TIMEOUT_COUNT + 1
					time.sleep(3)
		LogUtil.end_log()

	# void 初始化起始URL
	def initStartUrl(self):
		# 修改这里获取起始URL的途径
		self.start_url = ["https://list.jd.com/list.html?cat=670,671,672"]
		self._hostInfo = self.parseUrl(self.start_url[0])
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
	def initRules(self):
		# 获取url规则数组
		self._rules = Rules()
		if(not self._rules.isManual()):
			arr = self.getRulesFromMGDB()
			# 如果能获取到数据，说明用户在web前台填写了url规则
			if arr is not None:
				self._rules.initRules(arr)
		LogUtil.i("初始化Rules完成")

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
		# self._parser.setProto("http://") # 默认为https://，最好根据用户的输入智能设置 #
		# self._parser.setXpathBox(self._xpath.getXpath())
		# self._parser.setRules(self._rules)
		# self._parser.setQueue(self._queue)
		# self._parser.setBF(self._bf)
		# self._parser.setDomainFir(self._hostInfo["fir"]) # 传入一级域名
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

	
	# void 从数据库获取给定的xpath规则
	def getXpathFromMGDB(self):
		dic = {}
		dic["电影名"] = '//*[@id="content"]/h1/span[1]/text()'
		LogUtil.i("从数据库获取给定的xpath规则")
		return dic


	# void 从数据库获取给定的url规则
	def getRulesFromMGDB(self):
		LogUtil.i("从数据库获取给定的url规则")
		return ["https://list.jd.com/list.html?cat=670,671,672.*","https://item.jd.com/\d+.html"]

	# void 从数据库获取是否使用chrome-headless下载页面
	def getIfChromeEnable(self):
		LogUtil.i("从数据库获取是否使用chrome-headless下载页面")
		return True

	def start(self):
		print "线程数 4"
		for i in range(self._config["TREADING_COUNT"]):
			threading.Thread(target=self.run).start()

if __name__ == '__main__':

	project = Crystal("京东")
	project.start()
