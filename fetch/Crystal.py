#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re

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
		self._log = None

		self.initComponents()

	# 初始化各组件
	def initComponents(self):
		self._configer = Configer.getConfig()
		self._log = LogUtil()
		self.initStartUrl()
		self.initXpath()
		self.initRules()
		self.initDownloader()
		self.initBF()
		self.initQueue()
		self.initParser()

	# 运行
	def run(self):
		self._log.start_log()
		self.createDir(self._projectName)
		for each in self.start_url:
			self._queue.put(each)
		
		while not self._queue.empty():
			pagelink = self._queue.pop()
			parseRes = self.parseUrl(pagelink)
			if parseRes is None:
				host = None
				# 该url不合法
			else:
				host = parseRes["host"]
			page = self._downloader.get(pagelink)
			self._parser.process_item(host=host,pagelink=pagelink,page=page)
		
		self._log.end_log()

	def initStartUrl(self):
		self.start_url = ["https://www.jd.com"]
		self._hostInfo = self.parseUrl(self.start_url[0])
		self._log.i("初始化起始URL完成")

	# 初始化xpath
	def initXpath(self):
		# 获取name->xpath字典
		self._xpath = Xpath()
		if(not self._xpath.isManual()):
			dic = self.getXpathFromMGDB()
			self._xpath.initXpath(dic)
		self._log.i("初始化Xpath完成")

	# 初始化rules
	def initRules(self):
		# 获取url规则数组
		self._rules = Rules()
		if(not self._rules.isManual()):
			arr = self.getRulesFromMGDB()
			# 如果能获取到数据，说明用户在web前台填写了url规则
			if arr is not None:
				self._rules.initRules(arr)
		self._log.i("初始化Rules完成")
	# 初始化downloader
	def initDownloader(self):
		self._downloader = Downloader.getInstance()
		if( self.getIfChromeEnable() ):
			self._downloader.setChromeEnable(True)
		self._log.i("初始化Downloader完成")

	# void 初始化过滤器
	# - int -   number(可选) 过滤器最大过滤数
	# - float - errorRate(可选) 过滤器允许的哈希冲突率
	def initBF(self,number = 1000000,errorRate=0.0001):
		# if 配置文件中配置了过滤器的数目和错误率:
		# number = 
		# errorRate =
		self._bf = Bloomfilter(number,errorRate)
		self._log.i("初始化Filter完成")

	def initQueue(self):
		self._queue = Queue()
		self._log.i("初始化Queue完成")

	def initParser(self):
		self._parser = Parser()
		#self._parser.setProto("http://") # 默认为https://，最好根据用户的输入智能设置 #
		self._parser.setXpathBox(self._xpath.getXpath())
		self._parser.setRules(self._rules)
		self._parser.setQueue(self._queue)
		self._parser.setBF(self._bf)
		self._parser.setDomainFir(self._hostInfo["fir"]) # 传入一级域名
		self._log.i("初始化Parser完成")

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
				res["sub"] = None
				res["fir"] = match.group(3)
			else:
				res["sub"] = match.group(3)
				res["fir"] = match.group(5)
			res["all"] = match.group(0)
			res["proto"] = match.group(1)
			res["top"] = match.group(6)
			res["host"] = res["all"][len(res["proto"]):]
			return res
		else:
			return False
	
	# 创建工作目录
	def createDir(self,projectName):
		self.fileTool = File()
		self.fileTool.setDir(projectName)
		self._log.i("创建工作目录")

	
	# 从数据库获取给定的xpath规则
	def getXpathFromMGDB(self):
		dic = {}
		dic["商品名"] = '//*[@id="name"]/h1'
		dic["价格"] = '//*[@id="jd-price"]'
		self._log.i("从数据库获取给定的xpath规则")
		return dic
		pass

	# 从数据库获取给定的url规则
	def getRulesFromMGDB(self):
		self._log.i("从数据库获取给定的url规则")
		return None
		pass

	# 从数据库获取是否使用chrome-headless下载页面
	def getIfChromeEnable(self):
		self._log.i("从数据库获取是否使用chrome-headless下载页面")
		return True
		pass
if __name__ == '__main__':

	project = Crystal("京东")
	project.run()
