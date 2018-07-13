from __future__ import absolute_import
from celery import Celery
import os

#os.environ.setdefault('DJANGO_MAILBOX', 'Local')
#app = Celery('gnowsys_ndf',
#             include=['gnowsys_ndf.tasks'])

#app.config_from_object('gnowsys_ndf.celeryconfig')
app = Celery('gnowsys_ndf',
             broker='amqp://nroer_user:nroer_user123@127.0.0.1:5672/nroer_user_vhost',
             backend='rpc://',
             # include=['gnowsys_ndf.ndf.views.tasks']
            )
app.conf.update(
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
)
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gnowsys_ndf.settings')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

