#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import datetime
import codecs
import re
import multiprocessing as mp
from os import makedirs
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.proxy import *

list_id = '151304088'
list_url = 'http://music.163.com/#/playlist?id='+list_id
save_path = ""

from selenium import webdriver

options = webdriver.ChromeOptions()

options.binary_location = '/opt/google/chrome-unstable/google-chrome-unstable'

options.add_argument('headless')

options.add_argument('window-size=1200x600')

driver = webdriver.Chrome(chrome_options=options)



def createDir(list_name):
    global save_path
    save_path = u'歌单'+list_name.decode("utf-8")+u'歌词抓取'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 创建css样式文件
    with open(save_path+"/style.css","w+") as fp:
        fp.write("@media screen and (min-width:700px){#song{width:560px}}@media screen and (max-width:700px){#song{width:100%}}#song{font-size:18px;text-align:center;margin:0 auto}#author{margin:10px 0;font-size:24px}")

def processing(material):
    material = re.sub(r'<div class="crl">.*</div>', '', material, re.S)
    material = re.sub(r'<div id="flag_more" class="f-hide">','',material, re.S)
    material = re.sub(r'</div>','',material, re.S)
    head = '<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="style.css"></head><body><div id="song">'
    foot = '</div></body></html>'
    def wrapAuthor(matchobj):
        return '<div id="author">' + matchobj.group(0) + '</div>'
    material = re.sub(r'(作词 : .*?<br>)', wrapAuthor, material)
    lyric = (head + material + foot).encode('utf-8')
    return lyric

def getPlaylistName():
    list_name = driver.find_element_by_xpath('//h2[@class="f-ff2 f-brk"]').get_attribute("innerHTML").encode('utf-8')
    return list_name

def getMusicName():
    music_name = driver.find_element_by_xpath('//h2[@class="f-ff2 f-brk"]').get_attribute("innerHTML").encode('utf-8')
    return music_name

def getAllMusicLink():
    driver.switch_to_frame("g_iframe")
    list_name = getPlaylistName()
    createDir(list_name)
    urls = []
    names = []
    urlobjs = driver.find_elements_by_xpath('//div[@class="ttc"]/span[@class="txt"]/a')
    for url in urlobjs:
        url = url.get_attribute('href')
        urls.append(url)
    nameobjs = driver.find_elements_by_xpath('//div[@class="ttc"]/span[@class="txt"]/a/b')
    for name in nameobjs:
        name = name.get_attribute('title')
        names.append(name)
    assert(len(names) == len(urls))
    return zip(names, urls)

def getLyric(name,url):
    driver.get(url)
    log = raw_input("You say yes,And I start")
    driver.switch_to_frame("g_iframe")
    material = driver.find_element_by_id('lyric-content').get_attribute("innerHTML")
    lyric = processing(material)
    path = save_path+"/"+name+'.html'
    with open(path, "w+") as file:
        print("downloading: "+name.encode('GB18030'))
        file.write(lyric)

def run():
    driver.get(list_url)
    driver.maximize_window() # 将浏览器最大化显示
    
    allMusicZip = getAllMusicLink()
    for name,url in allMusicZip:
        getLyric(name,url)
        time.sleep(1) # 控制间隔时间，等待浏览器反映
    # driver.find_element_by_xpath('//a[@data-module="toplist"]').click()
    
    driver.close()

if __name__ == '__main__':
    print "start"
    start = datetime.datetime.now()
    run()
    end = datetime.datetime.now()
    print "end"
    print "time: ", end-start
