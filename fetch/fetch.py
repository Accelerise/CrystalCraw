#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
from lxml import etree

proto = 'http://';
host = 'www.amazon.cn'
start_url = 'https://www.amazon.cn/'
# 去除文件名中的非法字符 (Windows)
def validateTitle(title):
    rstr = ur"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    new_title = re.sub(rstr, "", title)
    return new_title
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

start_page = os.popen('google-chrome-unstable --headless --disable-gpu --dump-dom '+start_url)
raw_input("waiting")
res = start_page.read()
start_page.close()
dom = etree.HTML(res)
urls = dom.xpath('//a[not(contains(@href,"javascript"))]/@href')

# pools = re.findall(r'<a(.*?)</a>', res, re.S)
for url in urls:
	url = validateUrl(url,True)
	print ("url:"+url+'\n')
	# pools.append(url)
