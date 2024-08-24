from __future__ import absolute_import , unicode_literals
import os
from celery import Celery
from datetime import timedelta
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyConnectionSoftware.settings')
app = Celery('scheduler')
app.config_from_object('django.conf:settings',namespace='CELERY')

@app.task
def add_numbers():
    return

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.worker_main()

