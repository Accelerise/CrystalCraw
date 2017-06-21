#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import datetime
from lxml import etree
from Bloom import Bloomfilter
from Tool import Queue
from Tool import File
import Xpath
import Rules
import requests
import Downloader
import Parser
import Configer

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

		self.initComponents()

	# 初始化各组件
	def initComponents(self):
		self._configer = Configer.getConfig()
		self.initXpath()
		self.initRules()
		self.initDownloader()
		self.initBF()
		self.initQueue()
		self.initParser()

	# 运行
	def run():
		self.createDir(self.projectName)
		self.initComponents()
		start_url = []
		for each in start_url:
			self._queue.put(start_url)
		
		while not self._queue.empty():
			pagelink = self._queue.pop()
			host = self.extractHost()
			page = self._downloader.get(pagelink)
			self._parser.process_item(host=host,pagelink=pagelink,page=page)
		


	# 初始化xpath
	def initXpath():
		# 获取name->xpath字典
		self._xpath = Xpath()
		if(not self._xpath.isManual()):
			dic = self.getXpathFromMGDB("")
			self._xpath.initXpath(dic)

	# 初始化rules
	def initRules():
		# 获取url规则数组
		self._rules = Rules()
		if(not self._rules.isManual()):
			arr = self.getRulesFromMGDB("")
			# 如果能获取到数据，说明用户在web前台填写了url规则
			if arr is not None:
				self._rules.initRules(arr)
	# 初始化downloader
	def initDownloader():
		self._downloader = Downloader.getInstance()
		if( self.getIfChromeEnable() ):
			self._downloader.setChromeEnable(True)

	# void 初始化过滤器
	# - int -   number(可选) 过滤器最大过滤数
	# - float - errorRate(可选) 过滤器允许的哈希冲突率
	def initBF(self,number = 1000000,errorRate=0.0001):
		# if 配置文件中配置了过滤器的数目和错误率:
		# number = 
		# errorRate =
		self._bf = Bloomfilter(number,errorRate)

	def initQueue(self):
		self._queue = Queue()

	def initParser(self):
		self._parser = Parser()
		#self._parser.setProto("http://") # 默认为https://，最好根据用户的输入智能设置 #
		self._parser.setXpathBox(self._xpath.getXpath())
		self._parser.setRules(self._rules)
		self._parser.setQueue(self._queue)
		self._parser.setBF(self._bf)

	def extractHost(self,url):
		reobj = re.compile(r"""(?xi)\A
		[a-z][a-z0-9+\-.]*://                                # Scheme
		([a-z0-9\-._~%!$&'()*+,;=]+@)?                       # User
		([a-z0-9\-._~%]+                                     # Named or IPv4 host
		|\[[a-z0-9\-._~%!$&'()*+,;=:]+\])                    # IPv6+ host
		""")
		match = reobj.search(url)
		if match:
			return match.group(2)
		else:
			return False
	
	# 创建工作目录
	def createDir(self,projectName):
		self.fileTool = File()
		self.fileTool.setDir(projectName)

	
	# 从数据库获取给定的xpath规则
	def getXpathFromMGDB():
		pass

	# 从数据库获取给定的url规则
	def getRulesFromMGDB():
		pass

	# 从数据库获取是否使用chrome-headless下载页面
	def getIfChromeEnable():
		pass
if __name__ == '__main__':
	print "start"

	start = datetime.datetime.now()
	project = Crystal("京东")
	project.run()
	end = datetime.datetime.now()
	print "end"
	print "time: ", end-start