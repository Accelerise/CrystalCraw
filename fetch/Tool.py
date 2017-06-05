#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

class Queue:
    def __init__(self):
        self.items = []

    def empty(self):
        return self.items == []

    def put(self,item):
        ''''
        时间复杂度为 O(n)
        '''
        self.items.insert(0,item)

    def pop(self):
        '''
        时间复杂度为O(1)
        '''
        return self.items.pop()

    def size(self):
        return len(self.items)

class File:
	def __init__(self):
		pass
	# 创建文件夹
	def setDir(self,folder):
	    if not os.path.exists(folder):
	        os.makedirs(folder)
	    self.save_path = folder+"/"
	# 文件写入
	def fileIn(self,filename,content):
		path = self.save_path + filename
		with open(path, "w+") as fp:
			fp.write(content)