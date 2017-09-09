# -*- coding: utf-8 -*-
from django.conf.urls import url
import views

urlpatterns = [
	url(r'login$',views.login),
    url(r'setSpider$',views.setSpider),
    url(r'getSpider$',views.getSpider),
    url(r'getDoSpider$',views.getDoSpider),
    url(r'getAllData$',views.getAllData),
    url(r'getSpiderData$',views.getSpiderData),
    url(r'getWorker$',views.getWorker),
    url(r'getMessageFromId$',views.getMessageFromId),
    url(r'changeSpiderWorker$',views.changeSpiderWorker),
    url(r'closeSpider$',views.closeSpider),
    url(r'startSpider$',views.startSpider)
]