from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import SignupUserForm
from .models import UserForm,FormSample,ROLES,FormTransition,User
import json
import base64
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect('dashboard')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request,'there was an error logging in, try again')
            return  render(request, 'dashboard/login.html')
    else:
        return render(request, 'dashboard/login.html')
    
def logout_user(request):
    logout(request)
    messages.success(request,'Logged out successfully')
    return redirect("login")

def signup_user(request):
    if request.method == "POST":
        form = SignupUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request,user)
            messages.success(request,'Signed up Successfully')
            return redirect('dashboard')
        else: 
            messages.error(request,'There was an error with your form')
            return render(request, 'dashboard/signup.html', context={'form': form})
    else:
        form = SignupUserForm()

        return render(request, 'dashboard/signup.html',{"form":form})
    
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, 'dashboard/dashboard.html',{'page':'dashboard'})



def dashboard_forms(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    all_sample_forms = list(FormSample.objects.all())
    user_forms = list(UserForm.objects.filter(created_by=request.user))
        
    for form in user_forms:
        form.sample.transitions = json.loads(form.sample.transitions)
        if form.fields.get('Execution Type'):
            form.et = 'urgent'
        else:
            form.et = 'nou'

    return render(request, 'dashboard/forms.html',{'page':'forms','user_forms':user_forms, 'form_samples':all_sample_forms})

def dashboard_new_form(request,form_title):
    if not request.user.is_authenticated:
        return redirect("login")
    
    form_sample = FormSample.objects.filter(title=form_title).first()

    if request.method == "POST":
        
        finaldict = {}
        print(request.FILES)
        for filename, file in request.FILES.items():
            print(file)
            fs = FileSystemStorage()
            file_name = fs.save(file.name, file)
            file_url = fs.url(file_name)

            finaldict[filename]=file_url

        for key, value in dict(request.POST).items():
            if key == "csrfmiddlewaretoken":
                continue
            if request.FILES.get(key, False):
                file = request.FILES[key]
                print("sdf")
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_url = fs.url(filename)

                finaldict[key]=file_url
            else:
                finaldict[key] = value
        # print(finaldict)
        userform = UserForm.objects.create(created_by=request.user,sample=form_sample,fields=finaldict)

        tranisitions = [None,]
        # print(json.loads(form_sample.transitions))
        for trn in json.loads(form_sample.transitions):
            if trn == 'Department Moderator (Generic)':
                user_department = request.user.department
                if user_department:
                    tranisition = FormTransition.objects.create(form=userform,receivers_role=str(user_department.moderator.first_name + " " + user_department.moderator.last_name))
                else:
                    tranisition = FormTransition.objects.create(form=userform,receivers_role="CEO")

            elif trn in roles_filtered():
                tranisition = FormTransition.objects.create(form=userform,receivers_role=trn)
            else:
                tranisition = FormTransition.objects.create(form=userform,receivers_role=trn)

            tranisitions.append(tranisition)
            userform.all_transitions.add(tranisition)

        tranisitions.append(None)
        
        for prev, current, nxt in zip(tranisitions, tranisitions[1:], tranisitions[2:]):
            # print("HEREE: " + str(prev if prev else '') + "|"+ str(current if current else ''))
            current.prev_transition = prev if prev else None
            current.next_transition = nxt if nxt else None
            current.save()

        userform.current_transition = tranisitions[1]
        userform.save()

        # print(finaldict)
        return redirect("forms")

    
    
    for field in form_sample.fields:
        if field["field_type"] == 'radio' or field["field_type"] == 'checkbox':
            field['extra_details'] = field['extra_details'].split('\n')
    return render(request, 'dashboard/newform.html',{'page':'forms-admin','form_title':form_sample.title,'form_description':form_sample.description,"fields":form_sample.fields})
    
def roles_filtered():
    ROLES_filtered = []
    for r1, r2 in ROLES:
        ROLES_filtered.append(r1)
    return ROLES_filtered

def new_form_admin(request):
    if not request.user.is_authenticated:
        return redirect("login")
    ROLES_filtered = []
    for r1, r2 in ROLES:
        ROLES_filtered.append(r1)
    users = User.objects.all()
    return render(request, 'dashboard/newform-admin.html',{'page':'forms-admin','roles':ROLES_filtered,'users':users})

def dashboard_forms_admin(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        if (not request.POST["fields"]) or  (not request.POST["title"]) or (not request.POST["description"]):
            return HttpResponseBadRequest("One or more fields are not filled")

        fields = json.loads(request.POST["fields"])
        sample = FormSample.objects.create(fields=fields,description=request.POST["description"],title=request.POST["title"],transitions=request.POST['trns'],theme_color=request.POST['color'])
        
        return redirect("forms-admin")
    ROLES_filtered = []
    for r1, r2 in ROLES:
        ROLES_filtered.append(r1)
    if request.method == "GET":
        all_sample_forms = list(FormSample.objects.all())
        users = User.objects.all()
        for sample in all_sample_forms:
            sample.fields = json.loads(sample.fields) if issubclass(type(sample.fields), str) else sample.fields
            sample.fields_str = json.dumps(sample.fields)
            sample.transitions = json.loads(sample.transitions)
            sample.transitions_user = sample.transitions if issubclass(type(sample.transitions), str) else json.dumps(sample.transitions)
            trns_copy = list(sample.transitions)
            for index, trn in enumerate(sample.transitions) :
                if trn.isnumeric():
                    user = User.objects.get(pk=trn)
                    trns_copy[index] = user.first_name + " " +user.last_name 
            # print(all_sample_forms.transitions_str)
            print(sample.transitions)
            sample.transitions_str = trns_copy if issubclass(type(trns_copy), str) else json.dumps(trns_copy)
        return render(request, 'dashboard/forms-admin.html',{'page':'forms-admin',"formsamples":all_sample_forms,"roles":ROLES_filtered,  'users' : users})
        #     sample.transitions_str = sample.transitions if issubclass(type(sample.transitions), str) else json.dumps(sample.transitions)
        # return render(request, 'dashboard/forms-admin.html',{'page':'forms-admin',"formsamples":all_sample_forms,"roles":ROLES_filtered})

def dashboard_form_inbox(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        transition = UserForm.objects.get(pk=request.POST['formid']).current_transition
        if request.POST['comment']:
            transition.comment=request.POST['comment']
        
        # print(request.POST)
            
        if request.POST.get('role', False):
            if request.POST["role"].isdigit():
                print("sdf")
                user = User.objects.get(pk=request.POST["role"])
                transition.next_transition.receivers_role = user.first_name + " " + user.last_name
                transition.next_transition.save()

        # return
        if request.POST['action'] == 'accept':
            transition.status = 'ac'
            transition.sign = request.POST['sign']
            transition.save()
            UserForm.objects.filter(pk=request.POST['formid']).update(current_transition=transition.next_transition) 
            if not transition.next_transition:
                UserForm.objects.filter(pk=request.POST['formid']).update(current_transition=None,status='sm') 


        elif request.POST['action'] == 'sendback':
            if not transition.prev_transition:
                return HttpResponseBadRequest()
            transition.status = 'sb'
            transition.save()
            UserForm.objects.filter(pk=request.POST['formid']).update(current_transition=transition.prev_transition) 

        elif request.POST['action'] == 'decline':
            transition.status = 'dc'
            transition.save()
            UserForm.objects.filter(pk=request.POST['formid']).update(current_transition=None,status='dc') 
            
        elif request.POST['action'] == 'edit':
            transition.status = 'edit'
            transition.save()
            UserForm.objects.filter(pk=request.POST['formid']).update(current_transition=None,status='edit')


        return redirect("forms-inbox")
    
    transitions = FormTransition.objects.filter(Q(receivers_role=request.user.role)|Q(receivers_role=request.user.first_name + " " +request.user.last_name))

    forms_inbox = list(UserForm.objects.filter(Q(current_transition__receivers_role = request.user.role)|Q(current_transition__receivers_role = str(request.user.first_name + " " + request.user.last_name))))

    # Submitted forms
    submitted_forms=[]
    for trn in transitions:
        if trn.form not in forms_inbox:
            if trn.form.status == 'sm':
                submitted_forms.append(trn.form)
    submitted_forms = list(dict.fromkeys(submitted_forms)) # REMOVES DUPLICATES

    # Declined forms
    declined_forms=[]
    for trn in transitions:
        if trn.form not in forms_inbox:
            if trn.form.status == 'dc':
                print("sdf")
                declined_forms.append(trn.form)
    declined_forms = list(dict.fromkeys(declined_forms))

    if forms_inbox:
        for form in forms_inbox:
            form.fields = form.fields

    # On going forms
    ongoing_forms = []
    for trn in transitions:
        if trn.form not in forms_inbox:
            if trn.form.status == 'sm' or trn.form.status == 'dc':
                continue
            ongoing_forms.append(trn.form)
    ongoing_forms = list(dict.fromkeys(ongoing_forms))


    for form in ongoing_forms:
        form.sample.transitions = json.loads(form.sample.transitions)
        if form.fields.get('Execution Type'):
            form.et = 'urgent'
        else:
            form.et = 'nou'

    # for form in forms_inbox:
    #     if not form.current_transition:
    #         continue
    #     if form.current_transition.receivers_role.isnumeric():
    #         user = User.objects.get(pk=form.current_transition.receivers_role)
    #         form.current_transition.receivers_role = user.first_name + " " + user.last_name
    #     for index, trn in enumerate(form.all_transitions.all()):
    #         if trn.receivers_role.isnumeric():
    #             print(trn)
    #             user = User.objects.get(pk=trn.receivers_role)
    #             trn.receivers_role = user.first_name + " " + user.last_name
    
    
            
    return render(request, 'dashboard/forms-inbox.html',{"forms_inbox":forms_inbox, "ongoing_forms":ongoing_forms, 
                                                         "declined_forms":declined_forms , "submitted_forms":submitted_forms, 
                                                         'all_forms':[*submitted_forms, *ongoing_forms, *declined_forms, *forms_inbox] ,
                                                         'page':'forms-inbox'})

def get_role_users(request):
    print( request.GET)
    if request.GET['role']:
        return JsonResponse({"data":list(User.objects.filter(role=request.GET['role']).values())})
    
def dashboard_update_form(request,form_id):
    finaldict = {}
    for key, value in dict(request.POST).items():
        if key == "csrfmiddlewaretoken":
            continue
        finaldict[key] = value

    current_transition = UserForm.objects.get(pk=form_id).all_transitions.filter(status='edit').first()

    UserForm.objects.filter(pk=form_id).update(fields=finaldict,current_transition=current_transition,status='og')

    return redirect('forms')

def dashboard_forms_admin_update(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "GET":
       FormSample.objects.get(pk = request.GET['pk']).delete()
       return redirect('forms-admin')

    if request.method == "POST":
        print(request.POST)
        fields = json.loads(request.POST["fields"])

        FormSample.objects.filter(pk = request.POST['pk']).update(title=request.POST['title'],fields=fields,description=request.POST['description'],transitions=request.POST['trns'])
        return redirect('forms-admin')