#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver

import requests
from LogUtil import LogUtil

import threading
import time
import os
from Tool import Queue 

class Downloader:
	# 下载页面，提供两种方法 1.requests  2.chrome-headless
	_downloader = None
	# 默认使用requests
	chrome_enable = False

	# 构造函数
	def __init__(self):
		self.options = webdriver.ChromeOptions()
		self.options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'
		self.options.add_argument('headless')
		self.options.add_argument('window-size=1200x600')
		self.driver = webdriver.Chrome(chrome_options=self.options)
		# self.driver.set_page_load_timeout(10)  
		# self.driver.set_script_timeout(10)

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
		page = requests.get(url).content.decode("utf-8")
		return page

	# String 2.chrome-headless
	def getByChrome(self,url):
		self.driver.get(url)
		self.driver.quit()
		self.driver = webdriver.Chrome(chrome_options=self.options)
		self.driver.set_page_load_timeout(10)  
		self.driver.set_script_timeout(10)
		page = self.driver.find_elements_by_xpath("/html")[0].get_attribute("innerHTML")
		return page

	# void 关闭Chrome下载器
	def closeDownloader(self):
		self.driver.quit()

	# void 设置线程锁
	def setClock(lock):
		self.lock = lock

def doChore():
    time.sleep(0.5)

# Function for each thread
class multiDownload():
	# 构造函数
	def __init__(self,num,lock):
		self.max = num;
		self.options = webdriver.ChromeOptions()
		self.options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'
		self.options.add_argument('headless')
		self.options.add_argument('window-size=1200x600')
		self.cnt = 0
		self.lock = lock
		self.queue = Queue()
		# self.queue.put('http://www.accelerise.site')
		# self.queue.put('http://www.jd.com')

	def run(self):
		self.lock.acquire()
		LogUtil.start_log()
		self.lock.release()
		downloader = Downloader.getInstance()
		print Downloader.getInstance()
		downloader.setChromeEnable(True)
		self.lock.acquire()
		url = self.queue.pop()
		if not url:
			self.lock.release()
			return
		self.cnt = self.cnt + 1
		print self.cnt,url
		self.lock.release()
		downloader.get(url)

		downloader.closeDownloader()
		self.lock.acquire()
		LogUtil.end_log()
		self.lock.release()

	def start(self):
		for i in range(self.max):
			threading.Thread(target=self.run).start()

	def getMax(self):
		return self.max

if __name__ == '__main__':
	# Start 5 threads

	lock = threading.Lock()
	# lock = LogUtil.lock
	multi = multiDownload(5,lock)

	multi.queue.put('http://localhost')
	multi.queue.put('http://localhost')
	multi.queue.put('http://www.accelerise.site')
	multi.queue.put('http://www.jd.com')
	multi.queue.put('http://www.sina.com.cn/')

	multi.start()
	

