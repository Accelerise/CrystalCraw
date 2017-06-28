from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
import json
import pymongo
from models import DB
import traceback
from Crystal import Crystal
from collections import OrderedDict
from craw import spider
import time

def index(request):
    return render_to_response('index.html')


def loading(request):
    return render_to_response('loading.html')

@csrf_exempt
def start(request):
	dict = {}
	info = 'Data log save success'
	try:
		if request.method == 'POST':
			print request.body
			dict = json.loads(request.body,object_pairs_hook=OrderedDict)
			print dict
			startUrl = dict["mainUrl"]
			if(dict["detailUrl"]=="null"):
				detailUrl=None
			else:
				detailUrl=dict["detailUrl"]
			dict.pop("detailUrl")
			dict.pop("mainUrl")
			ans = "{'result':'work start'}"
			dbCrystalCraw = DB('127.0.0.1',27017)
			dbCrystalCraw.createDB("CrystalCraw")
			dbCrystalCraw.deleteAll("Status")
			dbCrystalCraw.deleteAll("Target")
			dbCrystalCraw.deleteAll("ids")
			dbCrystalCraw.deleteAll("Result")
			dbCrystalCraw.deleteAll("DataUrl")
			status = {"status":"start","id":1}
			dbCrystalCraw.insertDBforOne("Status",status)
			for key in dict:
				if(key.find("dataUrl")!=-1):
					document={"dataUrl":dict[key]}
					dbCrystalCraw.insertDBforOne("DataUrl",document)
					dict.pop(key)
			dbCrystalCraw.insertDB("Target",dict)
			dbCrystalCraw.createId()
			dbUrlCollect = DB('127.0.0.1', 27017)
			dbUrlCollect.createDB("UrlCollect")
			dbUrlCollect.deleteAll("Target")
			dbUrlCollect.deleteAll("ids")
			dbUrlCollect.createId()
			url=[]
			url.append(startUrl)
			init = Crystal("init")
			init.run("master",url,detailUrl)
			cur = 0
			end = dbUrlCollect.searchId()
			while cur < end:
				status = dbCrystalCraw.searchDataByRange("Status",1,1)
				flag = False
				for resp in status:
					if(resp["status"]=="stop"):
						flag = True
						break
				if (flag):
					break
				if(cur + 50 <= end):
					res = dbUrlCollect.searchDataByRange("Target",cur,cur+50)
					cur = cur+50
					url = []
					for document in res:
						url.append(document['url'])
					craw = spider.delay(url,detailUrl)
					i = 0
					while True:
						if craw.ready():
							print('craw:', craw.get())
							break
						else:
							print('wait...', i)
						time.sleep(1)
						i += 1
				else:
					res = dbUrlCollect.searchDataByRange("Target",cur,end)
					cur = end
					url = []
					for document in res:
						url.append(res['url'])
					craw = spider.delay(url,detailUrl)
					i = 0
					while True:
						if res.ready():
							print('res:', res.get())
							break
						else:
							print('wait...', i)
						time.sleep(1)
						i += 1
		ans = {"result":"start"}
		return HttpResponse(json.dumps(ans), content_type='application/json')

	except Exception, e:
		print 'str(Exception):\t', str(Exception)
		print 'str(e):\t\t', str(e)
		print 'repr(e):\t', repr(e)
		print 'e.message:\t', e.message


def stop(request):
	dbCrystalCraw = DB('127.0.0.1', 27017)
	dbCrystalCraw.createDB("CrystalCraw")
	dbCrystalCraw.motify("Status",{"id":1},{"status":"stop"})
	resp = {"result":"stop"}
	return HttpResponse(json.dumps(resp), content_type='application/json')


def getNumber(request):
	db = DB('127.0.0.1', 27017)
	db.createDB("UrlCollect")
	number = db.searchId()
	db.createDB("CrystalCraw")
	dataNumber=db.searchId()
	data = {}
	data["number"]=number
	data["dataNumber"]=dataNumber
	return HttpResponse(json.dumps(data),content_type="application/json")


def getData(request):
	db = DB('127.0.0.1', 27017)
	db.createDB("CrystalCraw")
	id = db.searchId()
	print id
	resData = db.searchDataByRange("Result", id, id)
	item = {}
	try:
		for res in resData:
			for key in res:
				item[key]=res[key]

	except Exception, e:
		print 'str(Exception):\t', str(Exception)
		print 'str(e):\t\t', str(e)
		print 'repr(e):\t', repr(e)
		print 'e.message:\t', e.message

	return HttpResponse(json.dumps(item), content_type='application/json')


def showResult(request):
	return render_to_response('results.html')

@csrf_exempt
def searchDataByRange(request):
	dict = json.loads(request.body, object_pairs_hook=OrderedDict)
	db = DB('127.0.0.1', 27017)
	db.createDB("CrystalCraw")
	ind=dict["index"]
	print ind
	sta = (ind-1)*48+1;
	end = ind*48
	id = db.searchId()
	if(end>id):
		end=id
	print end
	resData = db.searchDataByRange("Result", sta, end)
	ans = {}
	i=0
	try:
		for res in resData:
			i=i+1
			item = {}
			for key in res:
				if(key!="id"):
					item[key]=res[key]
			ans[res["id"]]=item
		print i

	except Exception, e:
		print 'str(Exception):\t', str(Exception)
		print 'str(e):\t\t', str(e)
		print 'repr(e):\t', repr(e)
		print 'e.message:\t', e.message

	return HttpResponse(json.dumps(ans), content_type='application/json')

def getCount(request):
	db = DB('127.0.0.1', 27017)
	db.createDB("CrystalCraw")
	id=db.searchId()
	ans={"number":id}
	return HttpResponse(json.dumps(ans), content_type='application/json')

@csrf_exempt
def searchByCol(request):
	if request.method=="POST":
		dict = json.loads(request.body, object_pairs_hook=OrderedDict)
		col=dict["col"]
		searchName=dict["searchName"]
		db = DB('127.0.0.1', 27017)
		db.createDB("CrystalCraw")
		resData = db.searchByName("Result", col, searchName)
		print resData
		ans = {}
		try:
			for res in resData:
				item = {}
				for key in res:
					if(key!="id"):
						item[key]=res[key]
				ans[res["id"]]=item
			print ans

		except Exception, e:
			print 'str(Exception):\t', str(Exception)
			print 'str(e):\t\t', str(e)
			print 'repr(e):\t', repr(e)
			print 'e.message:\t', e.message

		return HttpResponse(json.dumps(ans), content_type='application/json')