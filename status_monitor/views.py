from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime,now, timedelta
#from datetime import timedelta
from .models import  MonitoredSite, SiteCheckResult
from .forms import MonitoredSiteForm

#Begin user registration and authentication views
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse('home'))
    else:
        form = UserCreationForm()
        
    return render(request, 'status_monitor/register.html', {'form': form, 'title': 'Create Account'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect(request.POST.get('next') or 'home')
        messages.error(request, "Invalid username or password.")
        
    return render(request, 'status_monitor/login.html', {'next': request.GET.get('next', '')})
        
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

#Views for adding and editing sites
@login_required(login_url='login')
def site_list(request):
    sites = MonitoredSite.objects.filter(user=request.user)
    return render(request, 'status_monitor/site_list.html', {'sites': sites})

@login_required(login_url='login')
def site_create(request):
    if request.method == 'POST':
        form = MonitoredSiteForm(request.POST, user=request.user)
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            return redirect(reverse('status_page'))
    else:
        form = MonitoredSiteForm(user=request.user)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Add Site'})

@login_required(login_url='login')
def site_edit(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk,user=request.user)
    if request.method == 'POST':
        form = MonitoredSiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            return redirect(reverse('site_list'))
    else:
        form = MonitoredSiteForm(instance=site)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Edit Site'})

@login_required(login_url='login')
def site_delete(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk, user=request.user)
    if request.method == 'POST':
        site.delete()
        return redirect(reverse('status_page'))
    return render(request, 'status_monitor/site_confirm_delete.html', {'site': site})

@login_required(login_url='login')
def status_page(request):
    sites = MonitoredSite.objects.filter(user=request.user).order_by('-id').distinct()
    site_data = []

    for site in sites:
        checks = SiteCheckResult.objects.filter(site=site).order_by('-timestamp')[:20][::-1]
        latest_check=checks[-1] if checks else None
        timestamps = [c.timestamp.strftime("%H:%M") for c in checks]
        response_times = [c.response_time for c in checks]
        status_points = ["Up" if c.is_up else "Down" for c in checks]
        uptime = ((sum(1 for c in checks if c.is_up))/ len(checks) *100) if checks else 0
        
        site_data.append({
            'site' : site,
            'latest_check' : latest_check,
            'history' : checks,
            'timestamps' : timestamps,
            'response_times': response_times,
            'status_points' : status_points,
            'uptime' : uptime,
            
        })
        
    return render(request, "status_monitor/status_page.html", {"site_data": site_data})


def maintenance_page(request):
    return render(request, "status_monitor/maintenance_page.html")

def incidents_page(request):
    return render(request, "status_monitor/incidents_page.html")

@login_required(login_url='login')
def site_history(request,pk):
    site = get_object_or_404(MonitoredSite,pk=pk, user=request.user)
    checks = SiteCheckResult.objects.filter(site=site).order_by('timestamp')
    
    total_checks = checks.count()
    uptime = 0
    if total_checks > 0:
        uptime = checks.filter(is_up=True).count() / total_checks * 100
    
    timestamps = [c.timestamp.strftime("%Y-%m-%d %H:%M") for c in checks]
    response_times = [float(c.response_time or 0) for c in checks]
    status_points = ['Up' if c.is_up else "Down" for c in checks]
    
    context = { 
            'site' : site,
            'uptime' : uptime,
            'timestamps': timestamps,
            'response_times': response_times,
            'status_points': status_points
            }
    return render(request, 'status_monitor/site_history.html',context)
