from __future__ import absolute_import
from celery import Celery
app = Celery('myapp',
             broker='amqp://wcgfetch:wcgfetch@192.168.1.104:5672/wcg',
             backend='amqp://wcgfetch:wcgfetch@192.168.1.104:5672/wcg',
             include=['myapp.agent'])

app.config_from_object('myapp.config')

if __name__ == '__main__':
  app.start()