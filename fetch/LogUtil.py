#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import threading

class LogUtil:
	ENABLE_LEVEL = 5  #
	ERROR = 1
	WARNING = 2
	DEBUG = 3
	NOTICE = 4
	INFO = 5
	start = None
	end = None
	lock = threading.Lock()

	@classmethod
	def setLogLevel(cls,level):
		cls.ENABLE_LEVEL = level

	@classmethod
	def start_log(cls):
		cls.start = datetime.datetime.now()
		print "start~",cls.start

	@classmethod
	def end_log(cls):
		cls.end = datetime.datetime.now()
		used = cls.end - cls.start
		print " end ~",cls.end
		print "used ~",used
	# 打印日志 level : info
	@classmethod
	def i(cls,info):
		if cls.ENABLE_LEVEL >= LogUtil.INFO:
			nowdate = datetime.datetime.now()
			cls.lock.acquire()
			print "[Crystal|Info   ]~",nowdate,":"+info
			cls.lock.release()

	# 打印日志 level : notice
	@classmethod
	def n(cls,info):
		if cls.ENABLE_LEVEL >= LogUtil.NOTICE:
			nowdate = datetime.datetime.now()
			cls.lock.acquire()
			print "[Crystal|Notice ]~",nowdate,":"+info
			cls.lock.release()

	# 打印日志 level : debug
	@classmethod
	def d(cls,info):
		if cls.ENABLE_LEVEL >= LogUtil.DEBUG:
			nowdate = datetime.datetime.now()
			cls.lock.acquire()
			print "[Crystal|Debug  ]~",nowdate,":"+info
			cls.lock.release()

	# 打印日志 level : warning
	@classmethod
	def w(cls,info):
		if cls.ENABLE_LEVEL >= LogUtil.WARNING:
			nowdate = datetime.datetime.now()
			cls.lock.acquire()
			print "[Crystal|Warning]~",nowdate,":"+info
			cls.lock.release()

	# 打印日志 level : error
	@classmethod
	def e(cls,info):
		if cls.ENABLE_LEVEL >= LogUtil.ERROR:
			nowdate = datetime.datetime.now()
			cls.lock.acquire()
			print "[Crystal|Error  ]~",nowdate,":"+info
			cls.lock.release()
	
if __name__ == '__main__':
	print type(LogUtil)
	a = threading.Lock()
	b = threading.Lock()

	LogUtil.start_log()
	LogUtil.i("yes")
	LogUtil.w("喵喵喵?")
	LogUtil.i("出错啦!")
	LogUtil.end_log()