#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re

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
from models import DB
import json

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
		self.initComponents()

	# void 初始化各组件
	def initComponents(self):
		self._configer = Configer.getConfig()
		self.initStartUrl()
		self.initXpath()
		self.initRules()
		self.initDownloader()
		self.initBF()
		self.initQueue()
		#self.initParser()

	# void 运行
	def run(self,flag,targetUrl):
		LogUtil.start_log()
		self.createDir(self._projectName)
		self.setStartUrl(targetUrl)
		self.initParser()
		for each in self.start_url:
			self._queue.put(each.encode("UTF-8"))
		
		while not self._queue.empty():
			pagelink = self._queue.pop()
			parseRes = self.parseUrl(pagelink)
			if parseRes is None:
				host = None
				# 该url不合法
			else:
				host = parseRes["host"]
			page = self._downloader.get(pagelink)
			pagelink = pagelink.encode("UTF-8")
			if flag=="work":
				self._parser.process_item(host=host,pagelink=pagelink,page=page)
			elif flag=="master":
				self._parser.initCollectURLs(host=host, pagelink=pagelink, page=page)
		
		LogUtil.end_log()


	# void 初始化起始URL
	def initStartUrl(self):
		# 修改这里获取起始URL的途径
		self.start_url = ["http://localhost"]
		self._hostInfo = self.parseUrl(self.start_url[0])
		LogUtil.i("初始化起始URL完成")


	def setStartUrl(self, targetUrl):
		self.start_url = targetUrl
		self._hostInfo = self.parseUrl(self.start_url[0])
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
			# 如果能获取到数据，说明用户在web前台填写了url规则
			if arr is not None:
				self._rules.initRules(arr)
		LogUtil.i("初始化Rules完成")

	# void 初始化downloader
	def initDownloader(self):
		self._downloader = Downloader.getInstance()
		if( self.getIfChromeEnable() ):
			self._downloader.setChromeEnable(True)
		LogUtil.i("初始化Downloader完成")

	# void 初始化过滤器
	# - int -   number(可选) 过滤器最大过滤数
	# - float - errorRate(可选) 过滤器允许的哈希冲突率
	def initBF(self,number = 1000000,errorRate=0.0001):
		# if 配置文件中配置了过滤器的数目和错误率:
		# number = 
		# errorRate =
		self._bf = BloomFilter()
		LogUtil.i("初始化Filter完成")

	# void 初始化URL队列
	def initQueue(self):
		self._queue = Queue()
		LogUtil.i("初始化Queue完成")

	# void 初始化Parser
	def initParser(self):
		self._parser = Parser()
		#self._parser.setProto("http://") # 默认为https://，最好根据用户的输入智能设置 #
		self._parser.setXpathBox(self._xpath.getXpath())
		self._parser.setRules(self._rules)
		self._parser.setBF(self._bf)
		self._parser.setDomainFir(self._hostInfo["fir"]) # 传入一级域名
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



	def getXpathFromMGDB(self):
		db = DB("172.20.10.8",27017)
		db.createDB("CrystalCraw")
		res = db.searchData("Target")
		dict = {}
		i = 0
		for keyword in res:
			if(i % 2 == 0):
				att = keyword["attName"+str(i/2)]
			else:
				xpath =keyword["Xpath"+str(i/2)]
				dict[att]=xpath
			i = i + 1
		LogUtil.i("从数据库获取给定的xpath规则")
		return dict
		pass

	# void 从数据库获取给定的url规则
	def getRulesFromMGDB(self):
		LogUtil.i("从数据库获取给定的url规则")
		return None
		pass

	# void 从数据库获取是否使用chrome-headless下载页面
	def getIfChromeEnable(self):
		LogUtil.i("从数据库获取是否使用chrome-headless下载页面")
		return True
		pass
