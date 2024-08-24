from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.contrib.auth.forms import UserCreationForm
import json
import base64
from django.core.files.storage import FileSystemStorage
from django.db.models import Q

def suggestion_form(request):
    return render(request,'suggestions/suggestion-user.html', {'page':'suggestions'})
def add_new_suggestion(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        if (not request.POST["title"]) or (not request.POST["description"]):
            return HttpResponseBadRequest("One or more fields are not filled")
        sample = SuggestionSample.objects.create(user=request.user ,description=request.POST["description"] ,title=request.POST["title"])
        return redirect("dashboard")
def get_all_suggestion(request):
    data = SuggestionSample.objects.order_by('user','title')
    return render(request,'suggestions/suggestions-admin.html', {'page':'suggestions-admin', 'data' : data})