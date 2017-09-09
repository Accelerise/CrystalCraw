#!/usr/bin/env python
# -*- coding:utf-8 -*-
class Xpath:
	# 构造函数
	def __init__(self):
		self.xpath = {}
		#如要手动编写xpath，请在构造函数中实现
		#self.xpath["name"] = "xpath"

	# Bool 判断用户是否手动编写name-xpath
	def isManual(self):
		if self.xpath :
			return True
		else:
			return False

	# void 传入xpath字典初始化
	# - {} - dic xpath字典
	def initXpath(self,dic):
		for key in dic:
			if self.isXpath(dic[key]):
				if not self.isValidXpath(dic[key]):
					raise ValidXpath
			elif self.isCss(dic[key]):
				if not self.isValidCss(dic[key]):
					raise ValidCss
			self.xpath[key] = dic[key]

	# {} 返回xpath字典
	def getXpath(self):
		return self.xpath

	def isXpath(self,str):
		if str[0:1] == "/":
			return True
		else:
			return False
	def isValidXpath(self,str):
		if str[-2:] == "()":
			return True
		elif str.find("/@") != -1:
			return True
		else:
			return False

	def isCss(self,str):
		return False
	def isValidCss(self,str):
		return True

class ValidXpath(Exception):
	value="The Xpath you input is not Valid,Please check if you have add text() or other at the end of rule"
	"""docstring for XpathNotInit"""
	def __init__(self, value=""):
		super(Exception, self).__init__()
		if value is not "":
			self.value = value
	def __str__(self):
		return repr(self.value)

class ValidCss(Exception):
	value="The Css you input is not Valid,Please check rules"
	"""docstring for XpathNotInit"""
	def __init__(self, value=""):
		super(Exception, self).__init__()
		if value is not "":
			self.value = value
	def __str__(self):
		return repr(self.value)

if __name__ == '__main__':
	xpath = Xpath()

	if xpath.isManual():
		print "xpath是手动编写的"
	else:
		print "xpath不是手动编写的"

	dic = {'Name': '//a/@href', 'time': "//time/text()"}
	xpath.initXpath(dic)
	print xpath.getXpath()