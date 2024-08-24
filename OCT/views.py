
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import *
from dashboard.models import *
from dashboard.models import User
import json
from django.http import JsonResponse
from datetime import *
import csv
from django.db.models import Q
from djqscsv import render_to_csv_response

# Create your views here.
def dashboard_oc_tasks(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if not OCT.objects.filter(user=request.user).exists():
        OCT.objects.create(user=request.user)
    
    if request.method == "POST":
        if request.POST['type'] == 'daily':
            goal = OCT.objects.filter(user=request.user).first().monthly_tasks.filter(goal=request.POST['goal']).first()
            new_daily_task = DailyTasks.objects.create(topic=request.POST['topic'],estimated_time=request.POST['estimated'],goal_related_to=goal)
            OCT.objects.filter(user=request.user).first().daily_tasks.add(new_daily_task)
            return redirect('oc-tasks')

        if request.POST['type'] == 'monthly':
            new_monthly_task = MonthlyTasks.objects.create(goal=request.POST['goal'],description=request.POST['description'],progress_percentage=request.POST['progress'])
            OCT.objects.filter(user=request.user).first().monthly_tasks.add(new_monthly_task)
            return redirect('oc-tasks')

        print(request.POST)
    
    found_oct = OCT.objects.filter(user=request.user).first()
    monthly_tasks = list(found_oct.monthly_tasks.filter(Q(created_at__month=date.today().month) | ~Q(progress_percentage__in = ['100','100%','100 %'])))
    daily_tasks = list(found_oct.daily_tasks.filter(Q(created_at__gte=date.today()) | Q(status='nd')))
    daily_done = found_oct.daily_tasks.filter(status='done').count()
    daily_notdone = found_oct.daily_tasks.count() - daily_done

    return render(request, 'OCT/oc-tasks.html',{'page':'oc-tasks','daily_tasks':daily_tasks,"monthly_tasks":monthly_tasks,'daily_tasks_notdone':daily_notdone,"daily_tasks_done":daily_done})



def update_task(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        
        if request.POST['type'] == 'daily':
            mt = OCT.objects.filter(user=request.user).first().monthly_tasks.filter(goal=request.POST['goal']).first()

            OCT.objects.filter(user=request.user).first().daily_tasks.filter(pk=request.POST['pk']).update(topic=request.POST['topic'],estimated_time=request.POST['estimated'],goal_related_to=mt,status='edt')

            return redirect('oc-tasks')

        if request.POST['type'] == 'monthly':
            OCT.objects.filter(user=request.user).first().monthly_tasks.filter(pk=request.POST['pk']).update(goal=request.POST['goal'],progress_percentage=request.POST['progress'],description=request.POST['description'])
            return redirect('oc-tasks')


    if request.method == 'GET':
        found_oct = OCT.objects.filter(user=request.user).first()
        print(request.GET['type'])
        if request.GET['type'] == 'monthly':
            found_oct.monthly_tasks.filter(pk=request.GET['id']).delete()

        if request.GET['type'] == 'daily':
            found_oct.daily_tasks.filter(pk=request.GET['pk']).delete()

        # found_oct.daily_tasks.filter(id)
        return redirect("oc-tasks")
        
def close_task(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        
        if request.POST['type'] == 'daily':
            OCT.objects.filter(user=request.user).first().daily_tasks.filter(pk=request.POST['pk']).update(actual_time=request.POST['actual_time'],status='done',closed_at=datetime.now())

            return redirect('oc-tasks')

        if request.POST['type'] == 'monthly':
            OCT.objects.filter(user=request.user).first().monthly_tasks.filter(pk=request.POST['pk']).update(goal=request.POST['goal'],progress_percentage=request.POST['progress'],description=request.POST['description'])
            return redirect('oc-tasks')

def oc_admin(request):
    if not request.user.is_authenticated:
        return redirect("login")

    
    if request.user.is_superuser:
        users = list(User.objects.all())
    else:
        department = Department.objects.get(moderator=request.user)
        users = list(User.objects.filter(department=department))
        users.append(request.user)
    users_serialzed = []
    for user in users:
        oct = OCT.objects.filter(user=user).first()
        daily_done = oct.daily_tasks.filter(status='done').count()
        daily_notdone = oct.daily_tasks.count() - daily_done

        monthly_done = oct.daily_tasks.filter(status='done').count()
        monthly_notdone = oct.daily_tasks.count() - monthly_done

        

        serializer = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'last_login':user.last_login,
            'import_task' : len(OCT.objects.filter(user=user).first().daily_tasks.filter(created_at__date=datetime.today().date())) != 0,
            'daily_tasks':{'done':daily_done,"notdone":daily_notdone},
            'monthly_tasks':{'done':monthly_done,"notdone":monthly_notdone},
            'id':user.id
        }
        
        users_serialzed.append(serializer)
    # print(users_serialzed)
    
    return render(request, 'OCT/oc-admin.html',{'page':'oc-admin','users':users_serialzed,'today':datetime.today()})


def get_dailytasks(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    this_week = int(datetime.today().strftime("%U")) + 1 
    selected_week = this_week + int(request.GET['week']) if this_week + int(request.GET['week']) > 0 else 53 + this_week + int(request.GET['week'])
    print(datetime(2023,12,31).strftime("%U"))
    res_raw = OCT.objects.filter(user=request.GET['uid']).first().daily_tasks.filter(created_at__week=selected_week)

    final_res = {"Monday":[],"Tuesday":[],"Wednesday":[],"Thursday":[],"Friday":[],"Saturday":[],"Sunday":[]}
    for res in res_raw:
        serializer={
            "id":res.id,
            "status":res.get_status_display(),
            "topic":res.topic,
            "goal":res.goal_related_to.goal if res.goal_related_to else 'None',
            "estimated_time":res.estimated_time,
            "actual_time":res.actual_time,
            'checked_by_admin':res.checked_by_admin,
            "admin_comment":res.admin_comment,
            'ca_time':res.created_at.strftime("%H:%M:%S"),
            'ca_weekday':res.created_at.weekday(),
            'ca_weekdaystr':res.created_at.strftime("%A"),
            'ca_date':res.created_at.date(),

            'closed_time':res.closed_at.strftime("%H:%M:%S") if res.closed_at else '',
            'closed_weekday':res.closed_at.weekday() if res.closed_at else '',
            'closed_weekdaystr':res.closed_at.strftime("%A") if res.closed_at else '',
            'closed_date':res.closed_at.date() if res.closed_at else '',
        }
        final_res[res.created_at.strftime("%A")].append(serializer)


    return JsonResponse(final_res)

def get_monthlygoals(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    # this_month = datetime.today().date().month
    # print(this_month)
    
    res_raw = list(OCT.objects.filter(user=request.GET['uid']).first().monthly_tasks.filter(~Q(progress_percentage__in = ['100','100%','100 %'])).values())
    return JsonResponse({'data':res_raw})

def check_task(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if 'monthly' in request.GET:
        MonthlyTasks.objects.filter(pk=request.GET['tid']).update(checked_by_admin=True)
    else:
        DailyTasks.objects.filter(pk=request.GET['tid']).update(checked_by_admin=True)
    return JsonResponse({'data':"Successful"})


def comment_task(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    print(request.GET)
    selected_user = User.objects.get(pk=request.GET.get('uid'))
    if request.GET.get('type') == 'monthly':
        if request.GET.get('cmt'):
            OCT.objects.filter(user=selected_user).first().monthly_tasks.filter(pk=request.GET['tid']).update(admin_comment=f"{request.GET.get('cmt')}",checked_by_admin=True)
        else :
            OCT.objects.filter(user=selected_user).first().monthly_tasks.filter(pk=request.GET['tid']).update(admin_comment="",checked_by_admin=True)

    else:
        if request.GET.get('cmt'):
            OCT.objects.filter(user=selected_user).first().daily_tasks.filter(pk=request.GET['tid']).update(admin_comment=f"{request.GET.get('cmt')}",checked_by_admin=True)
        else :
            OCT.objects.filter(user=selected_user).first().daily_tasks.filter(pk=request.GET['tid']).update(admin_comment="",checked_by_admin=True)

    return JsonResponse({'data':"Successful"})

def export_excel(request):
    if not request.user.is_authenticated:
        return redirect("login")
    start_date = request.GET['start']
    end_date = request.GET['end']
    user_id = request.GET['user']
    print(request.GET)
    if request.GET['type'] == 'daily':
        user = User.objects.get(pk=user_id)
        query_set = OCT.objects.filter(user=user).first().daily_tasks.filter(created_at__range=[start_date,end_date]).values()
        # query_set.
        print(query_set)
        if not query_set:
            return HttpResponse('No Task Found')

        file_name =f"{user.username} Report ({start_date} to {end_date}).csv"  
        return render_to_csv_response(queryset=query_set,filename=file_name)

    elif request.GET['type'] == 'monthly':
            
        user = User.objects.get(pk=user_id)
        query_set = OCT.objects.filter(user=user).first().monthly_tasks.filter(created_at__range=[start_date,end_date]).values()
        # query_set.
        print(query_set)
        if not query_set:
            return HttpResponse('No Task Found')

        file_name =f"{user.username} Report ({start_date} to {end_date}).csv"  
        return render_to_csv_response(queryset=query_set,filename=file_name)
    

    elif request.GET['type'] == 'wh':
        start = request.GET['start'].split('-')
        end = request.GET['end'].split('-')
        start_date = date(int(start[0]),int(start[1]),int(start[2]))
        end_date = date(int(end[0]),int(end[1]),int(end[2]))
        
        user = User.objects.get(pk=user_id)
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{user.first_name + " " + user.last_name}.csv"'},
        )
        writer = csv.writer(response)

        writer.writerow(["Date", "Starting Time", "Ending Time"])

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)
        working_hours = []

        for day in daterange( start_date , end_date ):
            container = {'date':day, 'starting time':None, 'ending time':None}
            daily_tasks= OCT.objects.filter(user=user).first().daily_tasks.filter(created_at__date=day)
            if daily_tasks:
                container['starting time'] = daily_tasks.first().created_at.strftime("%H:%M:%S")

                for task in daily_tasks:
                    if container['ending time']:
                        container['ending time'] = task.closed_at if task.closed_at and task.closed_at > container['ending time'] else container['ending time']
                    else :
                        container['ending time'] = task.closed_at
                container['ending time'] = container['ending time'].strftime("%H:%M:%S") if container['ending time'] else "No Closed Task Found"

                working_hours.append(container)
                writer.writerow([container['date'], container['starting time'] , container['ending time']])

            
        print(working_hours)

        
        return response

def export_working_hours(request):
    if not request.user.is_authenticated:
        return redirect("login")
    start = request.GET['start'].split('-')
    end = request.GET['end'].split('-')

    start_date = date(int(start[0]),int(start[1]),int(start[2]))
    end_date = date(int(end[0]),int(end[1]),int(end[2]))
    user_id = request.GET['user']
    user = User.objects.get(pk=user_id)

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{user.first_name + user.last_name}.csv"'},
    )
    writer = csv.writer(response)

    writer.writerow(["Date", "Starting Time", "Ending Time"])

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    working_hours = []

    for day in daterange( start_date , end_date ):
        container = {'date':day, 'starting time':None, 'ending time':None}
        daily_tasks= OCT.objects.filter(user=user).first().daily_tasks.filter(created_at__date=day)
        if daily_tasks:
            container['starting time'] = daily_tasks.first().created_at.strftime("%H:%M:%S")

            for task in daily_tasks:
                if container['ending time']:
                    container['ending time'] = task.closed_at if task.closed_at and task.closed_at > container['ending time'] else container['ending time']
                else :
                    container['ending time'] = task.closed_at
            container['ending time'] = container['ending time'].strftime("%H:%M:%S") if container['ending time'] else "No Closed Task Found"

            working_hours.append(container)
            writer.writerow([container['date'], container['starting time'] , container['ending time']])

        
    print(working_hours)

    
    return response