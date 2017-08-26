#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os

parent_folder = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(parent_folder)
import settings

class Configer:
	@classmethod
	def getConfig(cls):
		return vars(settings)

if __name__ == '__main__':
	res = Configer.getConfig()
	print res