from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
import json
from OCT.models import OCT
# Create your models here.
ROLES = (
        ('Department Moderator (Generic)', 'Department Moderator (Generic)'),

        ('CEO', 'CEO'),
        ('Chief Officer', 'Chief Officer'),
        ('CEO Deligate', 'CEO Deligate'),

        ('CFO', 'CFO'),
        ('Accountant', 'Accountant'),

        ('Business Development Manager', 'Business Development Manager'),
        ('Business Development Expert', 'Business Development Expert'),
        ('Marketing Moderator', 'Marketing Moderator'),
        ('Marketing Expert', 'Marketing Expert'),

        ('IT Expert', 'IT Expert'),

        ('Technical Moderator', 'Technical Moderator'),
        ('Logistic Expert', 'Logistic Expert'),
        ('Factory', 'Factory'),
        ('QC Expert', 'QC Expert'),

        ('Solar Development', 'Solar Development'),
    )

DEPARTMENTS =(
    ('Finance', 'Finance'),
    ('Logistic', 'Logistic'),
    ('Supply & Marketing', 'Supply & Marketing'),
    ('Technical', 'Technical'),
    ('Sourcing', 'Sourcing'),
    ('QMS', 'QMS'),
    ('CEO', 'CEO'),
    ('IT', 'IT'),
)

class User(AbstractUser):
    email = models.CharField(max_length=80,unique=True)
    username = models.CharField(max_length=45,unique=True)

    first_name = models.CharField(max_length=45)
    last_name =  models.CharField(max_length=45)

    role = models.CharField(max_length=45, choices=ROLES)
    department = models.ForeignKey("Department",on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD="username"
    REQUIRED_FIELDS=['email',"first_name","last_name","role"]

    def fullname(self):
        return self.first_name + ' ' + self.last_name
    
    def is_moderator(self):
        if Department.objects.filter(moderator=self).exists():
            return True

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.pk:
            obj = super(User, self).save(*args, **kwargs)
            if not OCT.objects.filter(user=self).exists():
                OCT.objects.create(user=self)
            return obj


        return super(User, self).save(*args, **kwargs)


class Department(models.Model):
    department = models.CharField(max_length=45, choices=DEPARTMENTS)
    moderator = models.ForeignKey("User", related_name='moderator',on_delete=models.SET_NULL, null=True)
    def __str__(self) :
        return self.department
    
class FormTransition(models.Model):
    form = models.ForeignKey("UserForm", on_delete=models.CASCADE , null=True)
    # receiver_user = models.ForeignKey("User", related_name='receiver' , on_delete=models.CASCADE , null=True)
    receivers_role = models.CharField(max_length=150, choices=ROLES,null=True)

    sign = models.FileField(upload_to='uploads/', null=True)
    next_transition = models.ForeignKey('self', related_name='next', on_delete=models.CASCADE , null=True)
    prev_transition = models.ForeignKey('self', related_name='prev', on_delete=models.CASCADE , null=True)

    sender_user = models.ForeignKey("User", related_name='sender' , on_delete=models.CASCADE, null=True)

    STATUS_CHOICES = (
        ('edit','Must Be Edited'),
        ('sb','Sent Back'),
        ('ac', 'Accepted'),
        ('dc','Declined')
    )

    # upload = models.FileField(upload_to ='uploads')
    status = models.CharField(max_length=150,choices=STATUS_CHOICES,default='og',null=True)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    # def save(self, *args, **kwargs):
    #     if not self.pk and not self.receiver_role:
            
    #         self.receiver_role = self.receiver_user
    #         obj = super(FormTransition, self).save(*args, **kwargs)
    #         return obj
    #     return super(FormTransition, self).save(*args, **kwargs)
    def __str__(self):
        return str(self.form.id) +"| " + self.receivers_role + ( " ->" +self.next_transition.receivers_role if self.next_transition else "")

class UserForm(models.Model):
    created_by = models.ForeignKey("User", related_name='created_by' , on_delete=models.CASCADE)
    sample = models.ForeignKey("FormSample",related_name ="sample", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('og','On Going'),
        ('edit','Must Be Edited'),
        ('sm', 'Submitted'),
        ('dc','Declined')
    )
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,null=True,blank=True)
    
    # current_receiver = models.ForeignKey("User", related_name='current_receiver', on_delete=models.SET_NULL,blank=True, null=True)

    fields = models.JSONField(null=True) # Type: Value

    current_transition = models.OneToOneField(FormTransition, on_delete=models.CASCADE,null=True)
    all_transitions = models.ManyToManyField(FormTransition,related_name ="all_transitions")

    
    def __str__(self):
        return self.created_by.username + "/" + self.title

class FormSample(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    fields = models.JSONField(null=True) # Type: , Value:
    transitions = models.JSONField(null=True)
    theme_color = models.CharField(null=True,max_length=50)
    def __str__(self):
        return self.title + "/" + self.description