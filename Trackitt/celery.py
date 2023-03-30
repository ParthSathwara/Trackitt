from __future__ import absolute_import,unicode_literals
import os 
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Trackitt.settings')

app = Celery('celery_django')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/kolkata')

app.config_from_object(settings, namespace='CELERY')

# celery beat settings
app.conf.beat_schedule = {
    # 'every-10-seconds' : {
    # 'task': 'tracker.tasks.update_stocks',
    # 'schedule': 10,
    # 'args': ([['ADANIENT.NS','APOLLOHOSP.NS']])
    # },
}

# Load task modules from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')