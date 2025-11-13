from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.urls import reverse
from django.http import HttpResponseForbidden # NEW IMPORT
from .models import Site
from .forms import SiteForm
import json
import urllib.request, urllib.error
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse

# --- New Decorator to Enforce Configuration Permission ---
def configuration_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        # Check if the user is logged in AND their profile allows configuration
        if not request.user.is_authenticated or not request.user.userprofile.can_configure_sites:
            messages.error(request, "You no longer have permission to configure sites.")
            return redirect('site_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
# -------------------------------------------------------
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from datetime import timedelta
from .models import  MonitoredSite
from .forms import MonitoredSiteForm

#Begin user registration and authentication views
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('status_page'))
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse('status_page'))
    else:
        form = UserCreationForm()
        
    return render(request, 'status_monitor/register.html', {'form': form, 'title': 'Create Account'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('status_page'))
    
    form = AuthenticationForm(request, data= request.POST or None)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect(request.POST.get('next') or 'home')
        messages.error(request, "Invalid username or password.")
    context = {
        'form': form,
        'next': request.GET.get('next', ''),
    }
        
    return render(request, 'status_monitor/login.html', context)
        
def logout_view(request):
    if request.method == 'GET':
        return render(request, 'status_monitor/logout_confirm.html')
    
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have been logged out.")
        return redirect(reverse('login'))

@login_required(login_url='login')
def home(request):
    return redirect('status_page')
#checking site

def check_sites():
    sites = Site.objects.all()
    for site in sites:
        try: 
            start = timezone.now()
            #attempting to open sites URL with 5 second timeout
            with urllib.request.urlopen(site.url, timeout=5) as response:
                elapsed = (timezone.now()-start).total_seconds()
                site.response_time = elapsed
                site.status = "UP" if response.status == 200 else "DOWN"
        except urllib.error.URLError:
            site.status = "DOWN"
            site.response_time = 0.0

        #appending timestamp and response time
        current_time = timezone.now()
        site.timestamps.append(current_time.isoformat())
        site.response_times.append(round(site.response_time*1000,1))
        
        site.timestamps = site.timestamps[-720:]
        site.response_times = site.response_times[-720:]

        site.last_checked = timezone.now()
        site.save()
#Views for adding and editing sites (MODIFIED WITH DECORATOR)


@login_required(login_url='login')
def site_list(request):
    sites = MonitoredSite.objects.filter(user=request.user)
    return render(request, 'status_monitor/site_list.html', {'sites': sites})

@login_required(login_url='login')
@configuration_required # NEW DECORATOR APPLIED
def site_create(request):
    if request.method == 'POST':
        form = MonitoredSiteForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, " Site added successfully!")
            return redirect(reverse('site_list'))
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            return redirect(reverse('status_page'))
    else:
        form = MonitoredSiteForm(user=request.user)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Add Site'})

@login_required(login_url='login')
@configuration_required # NEW DECORATOR APPLIED
def site_edit(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk,user=request.user)
    if request.method == 'POST':
        form = MonitoredSiteForm(request.POST, instance=site, user=request.user)
        if form.is_valid():
            site=form.save(commit=False)
            site.user = request.user
            site.save()
            return redirect(reverse('status_page'))
    else:
        form = MonitoredSiteForm(instance=site,user=request.user)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Edit Site'})

@login_required(login_url='login')
@configuration_required # NEW DECORATOR APPLIED
def site_delete(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk, user=request.user)
    if request.method == 'POST':
        site.delete()
        return redirect(reverse('status_page'))
    return render(request, 'status_monitor/site_confirm_delete.html', {'site': site})

@login_required(login_url='login')
def status_page(request):
    #call function to perform site check
    check_sites()

    #get all site objects from database ordered alphabetically
    sites = Site.objects.all().order_by('url')
    #JSON updates
    if request.GET.get("json") == '1':
        site_list=[]
        for site in sites:
            site_list.append({
                "id": site.id,
                "timestamps": site.timestamps[-720:],
                "response_times" : [float(rt) for rt in site.response_times[-720:]],
            })
        return JsonResponse({"sites": site_list})
    
    #preparing JSON for charts
    for site in sites:
        #keeping only last 720 timestamps
        site.raw_timestamps = site.timestamps[-720:]
        site.response_times = site.response_times[-720:]

        #clean the responsee_time list
        site.response_times = [
            float(rt) for rt in site.response_times
            if isinstance(rt, (int, float, str)) and str(rt).replace('.', '', 1).isdigit()
        ]
        #converting timestamps to 12 hours
       
        site.timestamps_json = json.dumps(site.raw_timestamps)
        site.response_times_json = json.dumps(site.response_times)
        site.current_date = timezone.now().strftime("%b %d") #"ex Nove 12"
    return render(request, "status_monitor/status_page.html", {"sites": sites})

    sites = MonitoredSite.objects.filter(user=request.user).order_by('url').distinct()
    site_data = [site.get_status_summary(limit=20) for site in sites]
        
    return render(request, "status_monitor/status_page.html", {"site_data": site_data})

@login_required
def maintenance_page(request):
    return render(request, "status_monitor/maintenance_page.html")

@login_required
def incidents_page(request):
    return render(request, "status_monitor/incidents_page.html")

@login_required(login_url='login')
def site_history(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk, user=request.user)
    checks = site.check_results.order_by('timestamp')

    # Use the updated uptime method which requires checks
    uptime = site.calculate_uptime(checks)

    context = {
        'site': site,
        'uptime': uptime,
        'timestamps': [c.timestamp.isoformat() for c in checks],  # ISO timestamps
        'response_times': [float(c.response_time or 0) for c in checks],
        'status_points': ['Up' if c.is_up else 'Down' for c in checks],
    }
    return render(request, 'status_monitor/site_history.html', context)

@csrf_exempt
def set_timezone(request):
    if request.method == "POST":
        tz = request.POST.get("timezone")
        if tz:
            request.session["django_timezone"] = tz
            timezone.activate(tz)
        return HttpResponse(status=204)
    return HttpResponse(status=405)
