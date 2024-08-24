from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(UserForm)
admin.site.register(FormTransition)
admin.site.register(FormSample)
admin.site.register(Department)