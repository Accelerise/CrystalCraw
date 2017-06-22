#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lxml import etree
from Bloom import Bloomfilter
import Xpath
import re
from LogUtil import LogUtil

class Parser:
	# 解析页面，通用解析过程为1.收集url 2.尝试生成item，成功即插入数据库

	_parser = None

	# 构造函数
	# - String - proto(可选) 网站使用的协议 http:// / https://
	def __init__(self,proto="https://"):
		self.proto = proto
		self.xpathBox = None
		self.queue = None
		self.rules = None
		self.bf = None
		self.domainFir = None
		self.log = LogUtil()

	# Parser 单例模式
	@classmethod
	def getInstance(cls):
		if cls._parser is None:
			cls._parser = Parser()
		return cls._parser

	# void 修改协议
	# - String - proto 协议
	def setProto(self,proto):
		self.proto = proto

	# void 设置xpath规则
	# - {} -     dic xpath字典
	def setXpathBox(self,dic):
		self.xpathBox = dic

	# void 设置url规则
	# - {} -     dic url规则字典
	def setRules(self,dic):
		self.rules = dic

	# void 传入队列
	# - Queue -  queue 项目使用的url队列 
	def setQueue(self,queue):
		self.queue = queue

	# void 传入查重过滤器
	# - Queue -  queue 项目使用的url队列 
	def setBF(self,bf):
		self.bf = bf

	def setDomainFir(self,fir):
		self.domainFir = fir
		
	# void 通用页面解析
	# - String - host 页面host，url
	# - String - pagelink 页面源链接
	# - String - page 页面文档内容
	def process_item(self,host,pagelink,page):
		if self.xpathBox is None:
			raise XpathNotInit
		if self.queue is None:
			raise QueueNotInit
		if self.bf is None:
			raise BFNotInit
		self.log.i("开始解析页面："+pagelink)
		dom = etree.HTML(page)
		self.collectURLs(dom=dom,pagelink=pagelink,host=host)
		self.log.i("该页面收集URL结束："+pagelink)
		self.parseDetail(dom=dom,pagelink=pagelink,host=host)
		self.log.i("该页面详细分析结束："+pagelink)

		


	def collectURLs(self,dom,pagelink,host):
		urls = dom.xpath('//a[not(contains(@href,"javasc"))]/@href')
		for url in urls:
			url = self.standardizeUrl(host,url)
			if url is not False:
				if(not self.bf.isContain(url)):
					self.log.n("put in url:"+url+'\n')
					self.bf.add(url)
					self.queue.put(url)

	def parseDetail(self,dom,pagelink,host):
		item = {}
		item["xpath_fail_url"] = None
		first = True
		for key in self.xpathBox:
			if first:
				first = False
				res = dom.xpath(self.xpathBox[key])
				if len(res) is 1:
					item[key] = res[0]
				elif len(res) > 1:
					item[key] = res
				else:
					self.log.n("第一个就找不到，判定该页非详情页")
					# 第一个就找不到，判定该页非详情页
					return
			else:
				res = dom.xpath(self.xpathBox[key])
				if len(res) is 1:
					item[key] = res[0]
				elif len(res) > 1:
					item[key] = res
				else:
					self.log.n("找不到后面的，判断为xpath不够完善")
					# 找不到后面的，判断为xpath不够完善
					item["xpath_fail_url"] = pagelink
		if item["xpath_fail_url"] is None:
			# 数据库操作，插入数据item
			self.log.n("数据库操作，插入数据item")
			for key in item:
				self.log.n(key+' '+item[key])
			raw_input("我等等你")
		else:
			# 错误处理
			self.log.e("xpath提取错误处理")
			for key in item:
				self.log.n(key+' '+item[key])
			raw_input("我等等你")
	# String 清洗Url，使其标准化
	def standardizeUrl(self,host,url):
		# 清洗掉一级域名错误的url
		# 如 要爬取 （京东）www.jd.com 的数据 那么像 www.baidu.com 的url不会通过
		pat = re.compile(self.domainFir+r"\.")
		match = pat.search(url)
		if not match:
			return False
		# 给host拼接协议 
		# 如 www.amazon.cn => proto+www.amazon.cn
		pat = re.compile(r'^(\w+?(\.\w+?))',re.S)
		url = pat.sub(self.proto + r'\1',url)
		# 给相对路径拼接协议（proto）和主机（host）
		# 如 /gp/help/display.html => proto+host+/gp/help/display.html
		pat = re.compile(r'^/([^/])')
		url = pat.sub(self.proto + host +r'/\1',url)
		# 给双斜杠拼接协议
		# 如 //channel.jd.com => proto+channel.jd.com
		pat = re.compile(r'^//',re.S)
		url = pat.sub(self.proto , url)
		# 使用给定的url规则匹配，默认所有url都会通过，即(.*)
		noProto = url[len(self.proto):]
		if self.rules.match(noProto):
			return url
		else:
			return False

class XpathNotInit(Exception):
	value="You have not initialized XpathBox,please call setXpathBox(dic) and pass a Xpath in"
	"""docstring for XpathNotInit"""
	def __init__(self, value=""):
		super(Exception, self).__init__()
		if value is not "":
			self.value = value
	def __str__(self):
		return repr(self.value)
		
class QueueNotInit(Exception):
	value="You have not initialized Queue,please call setQueue(queue) and pass a Queue in"
	"""docstring for XpathNotInit"""
	def __init__(self, value=""):
		super(Exception, self).__init__()
		if value is not "":
			self.value = value
	def __str__(self):
		return repr(self.value)

class BFNotInit(Exception):
	value="You have not initialized BloomFilter,please call setBF(bf) and pass a BloomFilter in"
	"""docstring for XpathNotInit"""
	def __init__(self, value=""):
		super(Exception, self).__init__()
		if value is not "":
			self.value = value
	def __str__(self):
		return repr(self.value)

if __name__ == '__main__':
	parser = Parser()
	host = "www.jd.com"
	pagelink = "http://"
	page = ""
	parser.process_item(host,pagelink,page)
