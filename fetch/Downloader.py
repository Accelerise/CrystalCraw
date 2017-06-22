#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import requests

class Downloader:
	# 下载页面，提供两种方法 1.requests  2.chrome-headless
	_downloader = None
	# 默认使用requests
	chrome_enable = False

	# 构造函数
	def __init__(self):
		options = webdriver.ChromeOptions()
		options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'
		options.add_argument('headless')
		options.add_argument('window-size=1200x600')
		self.driver = webdriver.Chrome(chrome_options=options)
		self.driver.get("http://localhost")

	# 单例模式
	@classmethod
	def getInstance(cls):
		if cls._downloader is None:
			cls._downloader = Downloader()
		return cls._downloader

	# 下载页面
	def get(self,url):
		page = ""
		if self.chrome_enable :
			page = self.getByChrome(url)
		else:
			page = self.getByRequests(url)
		return page

	# 开启使用chrome-headless
	def setChromeEnable(self,enable):
		self.chrome_enable = enable

	# 1.requests
	def getByRequests(self,url):
		page = requests.get(url).content.decode("utf-8")
		return page

	# 2.chrome-headless
	def getByChrome(self,url):
		self.driver.get(url)
		page = self.driver.find_elements_by_xpath("/html")[0].get_attribute("innerHTML")
		return page

	def closeDownloader(self):
		if self.chrome_enable :
			self.driver.quit()



if __name__ == '__main__':
	downloader = Downloader.getInstance()
	print Downloader.chrome_enable
	print downloader.chrome_enable
	print downloader.get("http://localhost")
	downloader.setChromeEnable(True)
	print Downloader.chrome_enable
	print downloader.chrome_enable
	print downloader.get("http://localhost")

