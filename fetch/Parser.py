#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lxml import etree
from Bloom import Bloomfilter
import Xpath
import re

class Parser:
	# 解析页面，给出两种通用解析：1.收集url 2.分析详情页并收集url
	# 用户也可以编写自己的解析方法

	_parser = None

	def __init__(self,proto):
		self.proto = proto
		self.createBF()

	# 单例模式
	def getInstance():
		if _parser is None:
			_parser = Parser("https://")
		return _parser

	# 修改协议
	def setProto(self,proto):
		self.proto = proto

	# 设置xpath规则
	def setXpathBox(self,dict):
		self.xpathBox = dict

	# 初始化队列
	def createBF(self,number = 1000000,errorRate=0.0001):
		# if 配置文件中配置了过滤器的数目和错误率:
		# number = 
		# errorRate =
		self.bf = Bloomfilter(number,errorRate)

	# 1.收集url
	def process_collection(self,host,page):
		dom = etree.HTML(page)
		urls = dom.xpath('//a[not(contains(@href,"javasc"))]/@href')
		for url in urls:
				url = self.validateUrl(host,url)
				if(not self.bf.isContain(url)):
					print ("put in url:"+url+'\n')
					self.bf.add(url)

	# 2.分析详情页并收集url
	def process_item(self,host,page):
		dom = etree.HTML(page)
		item = {}
		for key in self.xpathBox:
			try:
				item[key] = dom.xpath(self.xpathBox[key])
			except:
				# 这个xpath不够完善

	# 修正Url格式
	def validateUrl(self,host,url):
		# 给host拼接协议 
		# 如 www.amazon.cn => proto+www.amazon.cn
		pat = re.compile(r'^(\w+?(\.\w+?))',re.S)
		url = pat.sub(self.proto + r'\1',url)
		# 给相对路径拼接协议（proto）和主机（host）
		# 如 /gp/help/display.html => proto+host+/gp/help/display.html
		pat = re.compile(r'^/([^/])')
		url = pat.sub(self.proto + self.host +r'/\1',url)
		# 给双斜杠拼接协议
		# 如 //channel.jd.com => proto+channel.jd.com
		pat = re.compile(r'^//',re.S)
		url = pat.sub(self.proto , url)

		return url

if __name__ == '__main__':
	xpath = Xpath()

	if xpath.isManual():
		print "xpath是手动编写的"
	else:
		print "xpath不是手动编写的"

	dict = {'Name': '//a/@href', 'time': "//time/text()"}
	xpath.initXpath(dict)
	print xpath.getXpath()
