# WCGfetcher:分布式爬虫平台

## 概览
WCGfetcher是一个分布式的爬虫平台。
用户无需编写代码，只需输入几个必要的参数即可从绝大多数博客类和电商类网站爬取结构化数据。
用户交互基于B/S结构，爬虫使用了多线程，Redis，Celery,MongoDB，Chrome-headless，Bloom过滤等技术。

## 环境要求
+ 操作系统Ubuntu 16.04
+ python 2.7

## 架构设计
<img src="screenshots/system.jpg" width="810" height="561"/>

总体工作流程

1.	前端获取包括起始URL、dataURL、detailURL、内容的名称和Xpath信息。
2.	Python后端获取到信息，初始化MongoDB数据库。
3.	开启爬虫模块先爬取一次满足规则的URL，通过Bloom去重后作为任务队列的初始化内容。
4.	Python后端将消费者需要的任务通过Celery的Broker分配给消费者。
5.	消费者获取任务开始爬取，如果碰到符合详情页规则的页面则开始具体分析，将分析结果放入存储结果的MongoDB数据库，同时把消费者运行的日志信息同时保存到数据库中。
6.	重复4，5直到队列无新的任务后停止。
7.	前端可以随时通过请求后端获得当前数据库存储的数据


## 爬虫流程
<img src="screenshots/crawler.png" width="695" height="712"/>

爬虫工作流程

1.	获取URL
1.	下载HTML文档
1.	收集a标签
1.	清洗去重URL
1.	URL进入队列
1.	分析HTML文档
1.	爬取结果存入数据库

## 项目目录
```
|-- wcgfetch						//分布式爬虫
|   |--backend						//web后端模块
|      |--models,py					//数据库封装
|      |--task.py					//任务分发
|      |--urls.py					//web路由
|      |--views.py 					//后端接口
|   |--frontend
|      |--dist 						//前端页面
|   |--craw 						//爬虫模块         
|   |--myapp						//celery启动模块
|-- fetch						//单例爬虫Crystal
```


## 参数详解

+ 起始URL ：作为初始链接，需要一个完整的url，完整至http。（必填）
+ 详情页URL：详情页链接url的正则表达示（可选），不填即把所有链接都当详情页搜索数据
+ 数据范围URL：用于限制爬取范围的url正则表达式（可选），如限制范围为京东笔记本，则填写https://list.jd.com/list.html\?cat=670,671,672.*
+ Xpath/CSS规则： 想要爬取的属性的名称及对应的搜索依据（必填）
如京东，
'商品名' 对应 xpath /html/body/div[5]/div/div[2]/div[1]/text() 或对应 CSS div.sku-name
'价格' 对应 xpath /html/body/div[5]/div/div[2]/div[3]/div/div[1]/div[2]/span/span[2]/text() 或对应 CSS span.price


输入一个起始的网站地址，爬虫将以宽度优先的遍历顺序爬取网站中所有的链接。
给定想要抓取的元素的Xpath，爬虫就会在遍历过程中将匹配到的数据存入数据库。
如果用户指定了详情页的URL正则，那么爬虫就能更加精准地找到详情页。
如果用户指定了爬虫应该检索的URL正则，那么宽度优先搜索时的路径将更加准确，减少无关商品的录入。

## 使用方法

### 单例爬虫

进入fetch目录，打开Crystal.py文件，修改__main__方法中的参数，运行Crystal.py文件启动单例爬虫
同目录下打开CrawSetting.py文件可修改爬虫配置，目前只有DOWNLOAD_DELAY（下载延时），TREADING_COUNT（线程数），CHROME_ENABLE（启用chrome浏览器）三项配置可用


## 环境依赖

### URL去重
基于Redis的Bloom过滤器，需要安装Redis

### 结果存储
存储数据的MongoDB，需要安装MongoDB

### 任务队列
存储任务队列的MongoDB和Python后端位于同一台vps，需要MongoDB

### 消费者节点
消费者节点的生产环境部署参考python后端的部署

### 依赖安装：
1.	安装pip，sudo apt install python-pip
2.	安装Django，sudo pip install Django
3.	安装pymongo，sudo pip install pymongo
4.	安装lxml，sudo pip install lxml
4.	安装cssselect，sudo pip install cssselect
5.	安装redis，sudo pip install redis
6.	安装requests，sudo pip install requests
7.	安装selenium，sudo pip install selenium
8.	安装celery，sudo pip install celery
9.	安装chrome，下载chrome开发版，下载地址：[chrome开发版](https://www.google.com/chrome/browser/desktop/index.html?extra=devchannel)
下载需要翻墙，安装后可以在/opt/google/chrome-unstable/google-chrome-unstable处看到已经安装
11.	安装chromedricer至python执行文件的目录，如/usr/bin。先安装bsdtar，sudo apt-get install bsdtar。
12.	运行
```
PLATFORM=linux64 \
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE. \
curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip -o ~/1.zip 
```
先安装到桌面，解压后，运行sudo cp ~/Desktop/chromedriver /usr/bin/chromedriver

15.	配置数据库地址，在Crystal.py中的 getXpathFromMGDB和getRulesFromMGDB函数中需要配置存储数据的MongoDB的ip地址信息。
16.	在Parser.py中的 collectURLs和initCollectURLs函数中需要配置任务队列的MongoDB的ip信息。同时在parseDetail函数中需要配置存储数据的MongoDB的ip地址信息。
17.	在view.py中多处需要配置数据库地址，其中CrystalCraw相关的是存储数据的数据库，UrlCollect相关的是任务队列的数据库。

## 贡献者（排名不分先后）
+ [rebirthwyw](https://github.com/rebirthwyw)
+ [Accelerise](https://github.com/Accelerise)
+ [guanzhentian](https://github.com/guanzhentian)