from __future__ import absolute_import
from celery import Celery


#os.environ.setdefault('DJANGO_MAILBOX', 'Local')
app = Celery('gnowsys_ndf',
             include=['gnowsys_ndf.tasks'])

app.config_from_object('gnowsys_ndf.celeryconfig')


if __name__ == '__main__':
    app.start()
