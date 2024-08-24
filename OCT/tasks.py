from __future__ import absolute_import , unicode_literals
from celery import shared_task
from .models import DailyTasks


@shared_task
def og_status(task_id):
    dt = DailyTasks.objects.get(pk=task_id)
    dt.status = 'og'
    dt.save()

@shared_task
def daily_tasks_handle():
    for dt in DailyTasks.objects.all():
        if dt.status != 'done':
            dt.status= 'nd'
            dt.save()
        

