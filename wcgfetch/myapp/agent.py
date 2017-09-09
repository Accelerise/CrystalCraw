from __future__ import absolute_import
from myapp.celery import app
from craw.Crystal import Crystal

@app.task
def spider(taskId, targetUrl):
    work = Crystal("craw_task" + str(taskId), taskId)
    work.start_single("work",targetUrl)