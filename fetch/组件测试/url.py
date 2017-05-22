#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
urls = ['//channel.jd.com/outdoor.html','http://car.jd.com/','www.jd.com','/gp/help/customer/display.html/ref=footer_hp_fp_topup/459-1201203-5640422?ie=UTF8&nodeId=201522740']
proto = 'http://';
host = 'www.amazon.cn'
# 修正Url格式
def validateUrl(url,https):
	# 给host拼接协议 
	# 如 www.amazon.cn => proto+www.amazon.cn
	pat = re.compile(r'^(\w+?(\.\w+?))',re.S)
	url = pat.sub(proto + r'\1',url)
	# 给相对路径拼接协议（proto）和主机（host）
	# 如 /gp/help/display.html => proto+host+/gp/help/display.html
	pat = re.compile(r'^/([^/])')
	url = pat.sub(proto + host +r'/\1',url)
	# 给双斜杠拼接协议
	# 如 //channel.jd.com => proto+channel.jd.com
	pat = re.compile(r'^//',re.S)
	url = pat.sub(proto , url)

	return url
for url in urls:
	print validateUrl(url,https)