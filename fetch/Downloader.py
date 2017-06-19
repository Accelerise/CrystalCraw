#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import requests

class Downloader:
	# 下载页面，提供两种方法 1.requests  2.chrome-headless
	_downloader = None

	# 构造函数
	def __init__(self):
		self.options = webdriver.ChromeOptions()
		self.options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'
		self.options.add_argument('headless')
		self.options.add_argument('window-size=1200x600')
		self.driver = webdriver.Chrome(chrome_options=options)

	# 单例模式
	def getInstance():
		if _downloader is None:
			_downloader = Downloader()
		return _downloader


	# 1.收集url
	def getByRequests(self,url):
		page = requests.get(url).content.decode("utf-8")
		return page

	# 2.分析详情页并收集url
	def getByChrome(self,url):
		page = self.driver.get(url)
		self.driver.close()
		return page




if __name__ == '__main__':
	xpath = Xpath()

	if xpath.isManual():
		print "xpath是手动编写的"
	else:
		print "xpath不是手动编写的"

	dict = {'Name': '//a/@href', 'time': "//time/text()"}
	xpath.initXpath(dict)
	print xpath.getXpath()
