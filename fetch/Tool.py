#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

class Queue:
    def __init__(self):
        self.items = []

    # Bool 判断队列是否为空
    def empty(self):
        return self.items == []

    # void 推入一个元素
    # - Type - item 元素
    def put(self,item):
        ''''
        时间复杂度为 O(n)
        '''
        self.items.insert(0,item)

    # Type 弹出一个元素
    def pop(self):
        '''
        时间复杂度为O(1)
        '''
        if self.empty():
            return None
        else:
            return self.items.pop()
        

    # int 队列长度
    def size(self):
        return len(self.items)

class File:
	def __init__(self):
		pass
	# void 创建文件夹
    # - String - folder 文件夹路径
	def setDir(self,folder):
	    if not os.path.exists(folder):
	        os.makedirs(folder)
	    self.save_path = folder+"/"

	# void 文件写入
    # - String - filename 文件名
    # - String - content 写入内容
	def fileIn(self,filename,content):
		path = self.save_path + filename
		with open(path, "w+") as fp:
			fp.write(content)

if __name__ == '__main__':
    queue = Queue()
    queue.put("1dgdfg")
    queue.put("22222")
    queue.put("3sdjkf")

    print queue.pop()
    print queue.pop()
    print queue.pop()
    print queue.pop()