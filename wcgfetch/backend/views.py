# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
import json
import pymongo
import traceback
from collections import OrderedDict
import time
import random
from models import WCG
from task import Task

@csrf_exempt
def login(request):
    try:
        if request.method == 'POST':
            loginForm = json.loads(request.body,object_pairs_hook=OrderedDict)
            status = { "message":"fail" }
            if (loginForm['name'] == 'test' and loginForm['password'] == 'test'):
                status = { "message":"success" }
            return HttpResponse(json.dumps(status), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

@csrf_exempt
def setSpider(request):
    try:
        if request.method == 'POST':
            taskForm = json.loads(request.body, object_pairs_hook=OrderedDict)
            db = WCG()
            id = db.incId("task")
            taskForm['id'] = id
            db.insertDBforOne("task",taskForm)
            status = {"message": "success"}
            return HttpResponse(json.dumps(status), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

def getSpider(request):
    db = WCG()
    resData = db.searchData("task")
    dict = []
    for res in resData:
        dict.append(res)
    return HttpResponse(json.dumps(dict),content_type='application/json')

def getDoSpider(request):
    db = WCG()
    resData = db.searchDataByStatus("task","doing")
    dict = []
    for res in resData:
        dict.append(res)
    return HttpResponse(json.dumps(dict),content_type='application/json')

@csrf_exempt
def getAllData(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body,object_pairs_hook=OrderedDict)
            if ids=="" or ids is None:
                return HttpResponse(json.dumps([]]), content_type='application/json')
            db = WCG()
            collection = "result_task" + str(ids['id'])
            resData = db.searchData(collection)
            dict = []
            for res in resData:
                dict.append(res)
            return HttpResponse(json.dumps(dict), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

@csrf_exempt
def getSpiderData(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body,object_pairs_hook=OrderedDict)
            if ids=="" or ids is None:
                return HttpResponse(json.dumps([]]), content_type='application/json')
            db = WCG()
            resData = db.searchDataByRange("task", ids['id'], ids['id'])
            dict = {}
            for res in resData:
                res['collectUrl'] = db.searchId("collectUrl_task" + str(ids['id']))
                res['anlysisUrl'] = db.searchId("anlysisUrl_task" + str(ids['id']))
                res['dataNumber'] = db.searchId("dataNumber_task" + str(ids['id']))
                dict = res
            return HttpResponse(json.dumps(dict), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

def getWorker(request):
    status ={"number" : 3}
    return HttpResponse(json.dumps(status), content_type='application/json')

@csrf_exempt
def getMessageFromId(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body, object_pairs_hook=OrderedDict)
            if ids=="" or ids is None:
                return HttpResponse(json.dumps([]]), content_type='application/json')
            db = WCG()
            collection = "log_task" + str(ids['id'])
            resData = db.searchData(collection)
            dict = []
            for res in resData:
                dict.append(res)
        return HttpResponse(json.dumps(dict), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

@csrf_exempt
def changeSpiderWorker(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body, object_pairs_hook=OrderedDict)
            db = WCG()
            db.motify("task", {"id": ids['id']}, {"selectWorker": ids['selectWorker']})
            message = {'message':'success'}
        return HttpResponse(json.dumps(message), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

@csrf_exempt
def closeSpider(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body, object_pairs_hook=OrderedDict)
            db = WCG()
            db.motify("task", {"id": ids['id']}, {"status": "success"})
            message = {'message':'success'}
        return HttpResponse(json.dumps(message), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message

@csrf_exempt
def startSpider(request):
    try:
        if request.method == 'POST':
            ids = json.loads(request.body, object_pairs_hook=OrderedDict)
            res = {}
            for key in ids:
                if(key != 'id'):
                    res[key] = ids[key]
            db = WCG()
            db.motify("task", {"id": ids['id']}, res)
            db.createId("collectUrl_task" + str(ids['id']))
            db.createId("anlysisUrl_task" + str(ids['id']))
            db.createId("dataNumber_task" + str(ids['id']))
            db.createId("url_task" + str(ids['id']))
            db.createId("result_task" + str(ids['id']))
            db.createId("log_task" + str(ids['id']))
            db.createCollection("url_task" + str(ids['id']))
            db.createCollection("result_task" + str(ids['id']))
            db.createCollection("log_task" + str(ids['id']))
            db.createCollection("config_task" + str(ids['id']))
            task = Task(ids['id'])
            task.getTaskFromMGDB()
            collection = "config_task" + str(ids['id'])
            if task.method == "chrome":
                db.insertDBforOne(collection, {"CHROME_ENABLE":True})
            else:
                db.insertDBforOne(collection, {"CHROME_ENABLE":False})
            db.motify("task", {"id": ids['id']}, {"status": "doing"})
            task.initTask()
            task.startTask()
            db.motify("task", {"id": ids['id']}, {"status": "success"})
            message = {'message':'success'}
        return HttpResponse(json.dumps(message), content_type='application/json')
    except Exception, e:
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
