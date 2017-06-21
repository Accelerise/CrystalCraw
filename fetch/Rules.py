#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

class Rules:
	# 构造函数
	def __init__(self):
		self.rules = ["*"]
		#如要手动编写rules，请在构造函数中实现
		#self.rules.append("url_reg")

	# 判断用户是否手动编写rules
	def isManual(self):
		if(self.rules[0] is not "*"):
			return True
		else:
			return False

	# 传入参数初始化
	def initRules(self,arr):
		self.rules = []
		for rule in arr:
			self.rules.append(rule)

	# 得到rules字典
	def getRules(self):
		return self.rules

	# 判断url是否匹配
	def match(self,url):
		for rule in self.rules:
			pat = re.compile(rule)
			if pat.match(url):
				return True
		return False

if __name__ == '__main__':
	subject = 'http://www.rgexcook.com/gv/kj'

	reobj = re.compile(r"""(?xi)\A
	[a-z][a-z0-9+\-.]*://                                # Scheme
	([a-z0-9\-._~%!$&'()*+,;=]+@)?                       # User
	([a-z0-9\-._~%]+                                     # Named or IPv4 host
	|\[[a-z0-9\-._~%!$&'()*+,;=:]+\])                    # IPv6+ host
	""")
	match = reobj.search(subject)
	if match:
	    print match.group(2)