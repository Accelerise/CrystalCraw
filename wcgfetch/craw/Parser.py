#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lxml import etree
from Bloom import BloomFilter
import Xpath
import re
from LogUtil import LogUtil
from Model import WCG
import weakref

class Parser:
    # 解析页面，通用解析过程为1.收集url 2.尝试生成item，成功即插入数据库

    _parser = None

    # 构造函数
    # - String - proto(可选) 网站使用的协议 http:// / https://
    def __init__(self,crystal,proto="https://"):
        self.proto = proto
        self.crystal = weakref.ref(crystal)
        self.xpath = crystal._xpath
        self.xpathBox = crystal._xpath.getXpath()
        self.queue = crystal._queue
        self.rules = crystal._rules
        self.bf = crystal._bf
        self.lock = crystal._lock
        self.db = WCG()

        if self.xpathBox is None:
            raise XpathNotInit
        if self.queue is None:
            raise QueueNotInit
        if self.bf is None:
            raise BFNotInit

    # Parser 单例模式
    @classmethod
    def getInstance(cls):
        if cls._parser is None:
            cls._parser = Parser()
        return cls._parser


    # void 修改协议
    # - String - proto 协议
    def setProto(self,proto):
        self.proto = proto

    def setDomain(self,domainFir):
        self.domainFir = domainFir
    # void 通用页面解析
    # - String - host 页面host，url
    # - String - pagelink 页面源链接
    # - String - page 页面文档内容
    def process_item(self,host,pagelink,page):
        LogUtil.n("开始解析页面："+pagelink,self.crystal()._taskId)
        dom = etree.HTML(page)
        self.collectURLs(dom=dom,pagelink=pagelink,host=host)
        LogUtil.n("该页面收集URL结束："+pagelink,self.crystal()._taskId)
        self.parseDetail(dom=dom,pagelink=pagelink,host=host)
        LogUtil.n("该页面详细分析结束："+pagelink,self.crystal()._taskId)

    # void 收集URL
    # - String -  dom html文档
    # - String -  pagelink 本页链接，用于调试时参考
    # - String -  host 本页host，用于拼接URL
    def collectURLs(self,dom,pagelink,host):
        LogUtil.n("开始初始化爬出url："+pagelink,self.crystal()._taskId)
        urls = dom.xpath('//a[not(contains(@href,"javasc"))]/@href')
        for url in urls:
            url = self.standardizeUrl(host,url)
            if url is not False:
                if(not self.bf.isContains(url)):
                    LogUtil.i("put in url:" + url + '\n')
                    self.bf.add(url)
                    self.db.incId("collectUrl_task"+str(self.crystal()._taskId))
                    collection = 'url_task'+str(self.crystal()._taskId)
                    id = self.db.incId(collection)
                    document = {"id":id,"url":url}
                    self.db.insertDBforOne(collection, document)

    def initCollectURLs(self, host, pagelink, page):
        LogUtil.n("开始初始化爬出url："+pagelink,self.crystal()._taskId)
        dom = etree.HTML(page)
        urls = dom.xpath('//a[not(contains(@href,"javasc"))]/@href')
        for url in urls:
            url = self.standardizeUrl(host, url)
            if url is not False:
                if (not self.bf.isContains(url)):
                    LogUtil.n("put in url:" + url + '\n')
                    self.bf.add(url)
                    self.db.incId("collectUrl_task"+str(self.crystal()._taskId))
                    collection = 'url_task'+str(self.crystal()._taskId)
                    id = self.db.incId(collection)
                    document = {"id":id,"url":url}
                    self.db.insertDBforOne(collection, document)


    # void 详细解析
    # - String -  dom html文档
    # - String -  pagelink 本页链接，用于调试时参考
    # - String -  host 本页host，用于拼接URL
    def parseDetail(self,dom,pagelink,host):
        self.db.incId("anlysisUrl_task"+str(self.crystal()._taskId))
        def innerHTML(node): 
            buildString = ''
            for child in node:
                buildString += etree.tostring(child, encoding="utf-8")
            return buildString
        def extractElement(key):
            res = []
            if self.xpath.isXpath(self.xpathBox[key]):
                tmp = dom.xpath(self.xpathBox[key])
                for each in tmp:
                    res.append(each.strip())
            else:
                tmp = dom.cssselect(self.xpathBox[key])
                for each in tmp:
                    if each.text is not None:
                        if each.text.strip() == "":
                            res.append(innerHTML(each).strip())
                        else:
                            res.append(each.text.strip())

            if len(res) is 1:
                return res[0]
            elif len(res) > 1:
                return res
            else:
                # 第一个就找不到，判定该页非详情页
                return None

        item = {}
        item["xpath_fail_url"] = None
        first = True
        if(self.rules.detailUrl!=None):
            flag = self.rules.matchDetail(pagelink)
            if(flag==False):
                return
        for key in self.xpathBox:
            if first:
                first = False
                item[key] = extractElement(key)
                if item[key] is None:
                    LogUtil.n("第一个就找不到，判定该页非详情页",self.crystal()._taskId)
                    #LogUtil.i("提取xpath："+self.xpathBox[key]+"，获取结果：")
                    return
            else:
                item[key] = extractElement(key)
                if item[key] is None:
                    LogUtil.n("找不到后面的，判断为xpath不够完善",self.crystal()._taskId)
                    item[key] = ""
                    # 找不到后面的，判断为xpath不够完善
                    item["xpath_fail_url"] = pagelink
            if type(item[key]) == list:
                item[key] = item[key][0]
            LogUtil.n("提取xpath："+self.xpathBox[key]+"，获取结果："+item[key],self.crystal()._taskId)

        if item["xpath_fail_url"] is None:
            collection = "result_task" + str(self.crystal()._taskId)
            id = self.db.incId(collection)
            document = {"id":id,"url":pagelink}
            for key in item:
                if (key!="xpath_fail_url"):
                    document[key] = item[key]
            self.db.insertDBforOne(collection,document)
            self.db.incId("dataNumber_task"+str(self.crystal()._taskId))
            LogUtil.i("数据库操作，插入数据item")
            #raw_input("我等等你")
        else:
            # 错误处理
            LogUtil.e("xpath提取错误处理")
            #raw_input("我等等你")

    # String / False 清洗Url，使其标准化
    # - String -  host 本页host，用于拼接URL
    # - String -  url 要清洗的URL
    def standardizeUrl(self,host,url):
        
        # 给host拼接协议
        # 如 www.amazon.cn => proto+www.amazon.cn
        pat = re.compile(r'^(\w+?(\.\w+?))',re.S)
        url = pat.sub(self.proto + r'\1',url)
        # 给相对路径拼接协议（proto）和主机（host）
        # 如 /gp/help/display.html => proto+host+/gp/help/display.html
        pat = re.compile(r'^/([^/])')
        url = pat.sub(self.proto + host +r'/\1',url)
        # 给双斜杠拼接协议
        # 如 //channel.jd.com => proto+channel.jd.com
        pat = re.compile(r'^//',re.S)
        url = pat.sub(self.proto , url)

        pat = re.compile(r'(.*)(#.*$)',re.S)
        url = pat.sub(r'\1' , url)
        # 清洗掉一级域名错误的url
        # 如 要爬取 （京东）www.jd.com 的数据 那么像 www.baidu.com 的url不会通过
        pat = re.compile(self.domainFir+r"\.")
        match = pat.search(url)
        if not match:
            return False
        # 使用给定的url规则匹配，默认所有url都会通过，即(.*)
        noProto = url[len(self.proto):]
        if self.rules.match(noProto):
            return url
        elif self.rules.match(url):
            return url
        else:
            return False

class XpathNotInit(Exception):
    value="You have not initialized XpathBox,please construct Parser with a complete Crystal instance"
    """docstring for XpathNotInit"""
    def __init__(self, value=""):
        super(Exception, self).__init__()
        if value is not "":
            self.value = value
    def __str__(self):
        return repr(self.value)

class QueueNotInit(Exception):
    value="You have not initialized Queue,please construct Parser with a complete Crystal instance"
    """docstring for XpathNotInit"""
    def __init__(self, value=""):
        super(Exception, self).__init__()
        if value is not "":
            self.value = value
    def __str__(self):
        return repr(self.value)

class BFNotInit(Exception):
    value="You have not initialized BloomFilter,please construct Parser with a complete Crystal instance"
    """docstring for XpathNotInit"""
    def __init__(self, value=""):
        super(Exception, self).__init__()
        if value is not "":
            self.value = value
    def __str__(self):
        return repr(self.value)

# if __name__ == '__main__':
# 	parser = Parser()
# 	host = "www.jd.com"
# 	pagelink = "http://"
# 	page = ""
# 	parser.process_item(host,pagelink,page)
