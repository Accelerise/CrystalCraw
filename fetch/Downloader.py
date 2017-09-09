#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import requests
from LogUtil import LogUtil

class Downloader:
	# 下载页面，提供两种方法 1.requests  2.chrome-headless
	_downloader = None
	# 默认使用requests
	chrome_enable = False

	# 构造函数
	def __init__(self):
		self.options = webdriver.ChromeOptions()
		self.options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'
		# self.options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
		self.options.add_argument('headless')
		self.options.add_argument('window-size=1200x600')
		self.options.add_argument('load-images=no')  ##关闭图片加载
		self.driver = webdriver.Chrome(chrome_options=self.options)
		# self.driver.set_page_load_timeout(8)  
		# self.driver.set_script_timeout(8)
		self.cnt = 0

	# 单例模式
	@classmethod
	def getInstance(cls):
		if cls._downloader is None:
			cls._downloader = Downloader()
		return cls._downloader

	# String 下载页面，返回html文档
	# - String -  url 要下载的页面链接
	def get(self,url):
		page = ""
		if self.chrome_enable :
			page = self.getByChrome(url)
		else:
			page = self.getByRequests(url)
		return page

	# void 开启使用chrome-headless
	# - Bool -  enable 是否启用chrome
	def setChromeEnable(self,enable):
		self.chrome_enable = enable

	# String 1.requests
	def getByRequests(self,url):
		LogUtil.n( str(self.cnt)+' '+url)
		self.cnt = self.cnt + 1
		page = requests.get(url).content.decode("utf-8")
		return page

	# String 2.chrome-headless
	def getByChrome(self,url):
		LogUtil.n( str(self.cnt)+' '+url)
		self.cnt = self.cnt + 1
		self.driver.get(url)
		page = self.driver.find_elements_by_xpath("/html")[0].get_attribute("innerHTML")
		self.driver.quit()
		self.driver = webdriver.Chrome(chrome_options=self.options)
		# self.driver.set_page_load_timeout(10)  
		# self.driver.set_script_timeout(10)
		return page

	# void 关闭Chrome下载器
	def closeDownloader(self):
		self.driver.quit()



if __name__ == '__main__':
	LogUtil.start_log()
	downloader = Downloader.getInstance()

	# downloader.setChromeEnable(True)
	downloader.get("http://localhost")
	downloader.get("http://localhost")
	downloader.get("http://www.accelerise.site")
	downloader.get("http://www.jd.com")
	downloader.get("http://www.sina.com.cn/")

	downloader.closeDownloader()
	LogUtil.end_log()

