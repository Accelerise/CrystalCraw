#coding=utf-8
from Crystal import Crystal
from celery import Celery


app = Celery('craw',
             broker='redis://127.0.0.1:6379/5',
             backend='redis://127.0.0.1:6379/5')


@app.task
def spider(url,detailUrl=None):
    worker=Crystal("craw")
    worker.run("work",url,detailUrl)
