from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_oc_tasks, name="oc-tasks"),
    path("update/", views.update_task, name="oc-update"),
    path("close/", views.close_task, name="oc-close"),

    path("admin/", views.oc_admin , name="oc-admin"),
    path("admin/dailytasks" , views.get_dailytasks, name='get-dailytasks'),
    path("admin/monthlygoals" , views.get_monthlygoals, name='get-monthlygoals'),
    
    path("admin/checktask" , views.check_task, name='checktask'),
    path("admin/commenttask" , views.comment_task, name='commenttask'),

    path("admin/export" , views.export_excel, name='export'),
    # path("admin/exportwh" , views.export_working_hours, name='export'),
]