from django.urls import path

from . import views

urlpatterns = [
    path("", views.suggestion_form, name="suggestions"),
    path("add/", views.add_new_suggestion, name="add-suggestions"),
    path("admin/", views.get_all_suggestion, name="suggestions-admin"),


    
]