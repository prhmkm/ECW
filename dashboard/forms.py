from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class SignupUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'role')
    def __init__(self, *args, **kwargs):
        super(SignupUserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'au-input au-input--full'