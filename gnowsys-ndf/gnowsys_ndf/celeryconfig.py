from datetime import timedelta
from gnowsys_ndf.local_settings import SYNCDATA_DURATION
BROKER_URL = 'amqp://'

CELERYBEAT_SCHEDULE = {
    'do-every-fixed-seconds': {
        'task': 'gnowsys_ndf.tasks.run_syncdata_script',
        'schedule': timedelta(seconds=SYNCDATA_DURATION),
        #'args': (16, 16)
    },
}

CELERY_TIMEZONE = 'UTC'

