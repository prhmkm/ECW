from django.db import models
from datetime import timedelta
from django.utils.timezone import now

# Create your models here. sdf
class OCT(models.Model):
    user = models.OneToOneField("dashboard.User", related_name='octuser' , on_delete=models.CASCADE)
    daily_tasks = models.ManyToManyField("DailyTasks",blank=True)
    monthly_tasks = models.ManyToManyField("MonthlyTasks",blank=True)

class MonthlyTasks(models.Model):
    goal = models.CharField(max_length=150)
    progress_percentage = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True,blank=True)
    admin_comment = models.CharField(max_length=150, null=True,blank=True)
    checked_by_admin = models.BooleanField(default=False)


    STATUS_CHOICES = (
        ('og','On Going'),
        ('done', 'Done'),
        ('nd','Not Done')
    )
    status = models.CharField(max_length=150,choices=STATUS_CHOICES,default='og')

    def __str__(self):
        return self.goal

class DailyTasks(models.Model):
    topic = models.CharField(max_length=150)
    estimated_time = models.CharField(max_length=150)
    actual_time = models.CharField(max_length=150, null=True,blank=True)
    goal_related_to = models.ForeignKey('MonthlyTasks',related_name='goal_related_to',on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin_comment = models.CharField(max_length=150, null=True,blank=True)
    checked_by_admin = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True,blank=True)

    STATUS_CHOICES = (
        ('jc','Just Created'),
        ('og','On Going'),
        ('edt', 'Edited'),
        ('done', 'Done'),
        ('nd','Not Done')
    )

    status = models.CharField(max_length=150,choices=STATUS_CHOICES,default='jc')
    def __str__(self):
        return self.topic

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         obj = super(DailyTasks, self).save(*args, **kwargs)
    #         from .tasks import og_status
    #         og_status.apply_async(args=[self.id],countdown=600)
    #         return obj
    #     return super(DailyTasks, self).save(*args, **kwargs)