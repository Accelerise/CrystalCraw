#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Xpath:
	# 构造函数
	def __init__(self):
		self.xpath = {}
		#如要手动编写xpath，请在构造函数中实现
		#self.xpath["name"] = "xpath"

	# 判断用户是否手动编写name-xpath
	def isManual(self):
		if self.xpath :
			return True
		else:
			return False

	#
	def initXpath(self,dict):
		for key in dict:
			self.xpath[key] = dict[key]

	#
	def getXpath(self):
		return self.xpath

if __name__ == '__main__':
	xpath = Xpath()

	if xpath.isManual():
		print "xpath是手动编写的"
	else:
		print "xpath不是手动编写的"

	dict = {'Name': '//a/@href', 'time': "//time/text()"}
	xpath.initXpath(dict)
	print xpath.getXpath()