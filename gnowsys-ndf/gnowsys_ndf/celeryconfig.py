from datetime import timedelta

BROKER_URL = 'amqp://'

CELERYBEAT_SCHEDULE = {
    'do-every-60-seconds': {
        'task': 'gnowsys_ndf.tasks.run_syncdata_script',
        'schedule': timedelta(seconds=60),
        #'args': (16, 16)
    },
}

CELERY_TIMEZONE = 'UTC'

