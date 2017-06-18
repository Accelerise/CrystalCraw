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

class Fetcher:
	# 构造函数
	def __init__(self,proto,host,start_url):
		self.proto = proto
		self.host = host
		self.start_url = start_url
		self.pools = Queue()

	# 初始化队列
	def createQueue(self,number = 10000000,errorRate=0.00001):
		self.bf = Bloomfilter(number,errorRate)
		self.bf.add(self.start_url)
	
	# 创建工作目录
	def createDir(self,projectName):
		self.fileTool = File()
		self.fileTool.setDir(projectName)

	# 去除文件名中的非法字符 (Windows)
	def validateTitle(title):
	    rstr = ur"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
	    new_title = re.sub(rstr, "", title)
	    return new_title
	# 修正Url格式
	def validateUrl(self,url):
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
	# 下载页面
	def download(self):
		import sys 
		reload(sys) 
		sys.setdefaultencoding('utf8')   
		self.pools.put(self.start_url)
		while not self.pools.empty():
			url = self.pools.pop()
			print ("downloading..."+url+'\n')
			page = os.popen('google-chrome-unstable --headless --disable-gpu --dump-dom '+url)
			res = page.read()
			page.close()
			global fNum
			fNum = fNum+1
			filename = "file" + str(fNum)+".html"
			self.fileTool.fileIn(filename,u"该页面来自"+url+"<br/>"+res)
			# 防止因报错而退出
			try:
				dom = etree.HTML(res)
				urls = dom.xpath('//a[not(contains(@href,"javasc"))]/@href')
			except :
			    pass

			if(fNum >= 30):
				break
			# self.pools = re.findall(r'<a(.*?)</a>', res, re.S)
			i = 0
			for url in urls:
				i = i+1
				url = self.validateUrl(url)
				if(not self.bf.isContain(url)):
					print ("put in url:"+url+'\n')
					self.pools.put(url)
					self.bf.add(url)

if __name__ == '__main__':
	print "start"

	start = datetime.datetime.now()
	projectName = u"京东"
	proto = 'https://'
	host = 'www.jd.com'
	start_url = 'https://item.jd.com/3819563.html'
	fNum = 0

	fetcher = Fetcher(proto,host,start_url)
	fetcher.createQueue()
	fetcher.createDir(projectName)

	fetcher.download()
	end = datetime.datetime.now()
	print "end"
	print "time: ", end-start