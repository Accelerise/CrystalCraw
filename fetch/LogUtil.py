#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime

class LogUtil:
	ENABLE_LEVEL = None
	ERROR = 5
	WARNING = 4
	DEBUG = 3
	NOTICE = 2
	INFO = 1
	# 构造函数
	def __init__(self,level=5):
		self.start = None
		self.end = None
		self.ENABLE_LEVEL = level

	def setLogLevel(self,level):
		self.ENABLE_LEVEL = level

	def start_log(self):
		self.start = datetime.datetime.now()
		print "start~",self.start

	def end_log(self):
		self.end = datetime.datetime.now()
		used = self.end - self.start
		print " end ~",self.end
		print "used ~",used
	# 打印日志 level : info
	def i(self,info):
		if self.ENABLE_LEVEL >= LogUtil.INFO:
			nowdate = datetime.datetime.now()
			print "[Crystal|Info   ]~",nowdate,":"+info

	# 打印日志 level : notice
	def n(self,info):
		if self.ENABLE_LEVEL >= LogUtil.NOTICE:
			nowdate = datetime.datetime.now()
			print "[Crystal|Notice ]~",nowdate,":"+info

	# 打印日志 level : debug
	def d(self,info):
		if self.ENABLE_LEVEL >= LogUtil.DEBUG:
			nowdate = datetime.datetime.now()
			print "[Crystal|Debug  ]~",nowdate,":"+info

	# 打印日志 level : warning
	def w(self,info):
		if self.ENABLE_LEVEL >= LogUtil.WARNING:
			nowdate = datetime.datetime.now()
			print "[Crystal|Warning]~",nowdate,":"+info

	# 打印日志 level : error
	def e(self,info):
		if self.ENABLE_LEVEL >= LogUtil.ERROR:
			nowdate = datetime.datetime.now()
			print "[Crystal|Error  ]~",nowdate,":"+info
	

if __name__ == '__main__':
	logUtil = LogUtil()
	print type(logUtil)
	logUtil.start_log()
	logUtil.i("yes")
	logUtil.w("喵喵喵?")
	logUtil.i("出错啦!")
	logUtil.end_log()