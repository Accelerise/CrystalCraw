#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Rules:
	# 构造函数
	def __init__(self):
		self.rules = {}
		#如要手动编写rules，请在构造函数中实现
		#self.rules["url"] = func

	# 判断用户是否手动编写rules
	def isManual(self):
		if(self.rules):
			return True
		else:
			return False

	# 传入参数初始化
	def initRules(self,dict):
		for key in dict:
			self.rules[key] = dict[key]

	# 得到rules字典
	def getRules(self):
		return self.rules

if __name__ == '__main__':
	rules = Rules()

	if rules.isManual():
		print "rules是手动编写的"
	else:
		print "rules不是手动编写的"

	def pipeline1():
		#写入数据库
		pass
	def pipeline2():
		#写入数据库
		pass

	dict = {'url1': pipeline1, 'url2': pipeline2, 'url3': None}
	rules.initRules(dict)
	print rules.getRules()