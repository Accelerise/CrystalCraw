#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

class Rules:
	# 构造函数
	def __init__(self):
		all = re.compile(".*")
		self.rules = [all]
		#如要手动编写rules，请在构造函数中实现
		#self.rules.append("url_reg")

	# Bool 初始时判断用户是否手动编写rules
	def isManual(self):
		if(len(self.rules) is not 1 ):
			return True
		else:
			return False

	# void 传入参数初始化
	# - Array - arr url规则数组
	def initRules(self,arr,detailUrl=None):
		self.rules = []
		for rule in arr:
			rule = re.compile(rule)
			self.rules.append(rule)
		self.detailUrl = detailUrl

	# Array 得到rules数组
	def getRules(self):
		return self.rules

	# Bool 判断url是否匹配dataUrl
	# - String - url 待匹配url
	def match(self,url):
		for rule in self.rules:
			match = rule.match(url)
			if match:
				return True
		return False

	# Bool 判断url是否匹配detailUrl
	# - String - url 待匹配url
	def matchDetail(self,url):
		pat=re.compile(self.detailUrl)
		match = pat.match(url)
		if match:
			return True
		return False

# if __name__ == '__main__':
# 	url = "www.jd."
# 	pat = re.compile("jd"+r"\.")
# 	match = pat.search(url)
# 	if not match:
# 		print "不匹配"
# 	else:
# 		print "匹配"
	
