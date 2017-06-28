"""back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import *
from django.conf.urls.static import static
from django.views.static import serve
import os
from . import view

urlpatterns = [
    url(r'^css/(?P<path>.*)$', serve,
        {'document_root': os.path.join(settings.STATIC_PATH, 'css')}),
    url(r'^fonts/(?P<path>.*)$', serve,
        {'document_root': os.path.join(settings.STATIC_PATH, 'fonts')}),
    url(r'^img/(?P<path>.*)$', serve,
        {'document_root': os.path.join(settings.STATIC_PATH, 'img')}),
    url(r'^js/(?P<path>.*)$', serve,
        {'document_root': os.path.join(settings.STATIC_PATH, 'js')}),
    url(r'^start/', view.start),
    url(r'getNumber/$',view.getNumber),
    url(r'getCount/$', view.getCount),
    url(r'getData/$', view.getData),
    url(r'searchByCol/$', view.searchByCol),
    url(r'stop/$',view.stop),
    url(r'searchDataByRange/$',view.searchDataByRange),
    url(r'^results/',view.showResult),
    url(r'^loading/',view.loading),
    url(r'^.*$', view.index),
]