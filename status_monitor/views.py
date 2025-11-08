from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from .models import Site, MonitoredSite, SiteCheckResult
from .forms import SiteForm

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
    
    context = {}
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            next_from_post = request.GET.get('next') or request.POST.get('next') or ''
            if next_from_post:
                return redirect(next_from_post)
            return redirect(reverse('home'))
        else:
            context['error'] = "Invalid username or password."
        
    context.setdefault('next', next_url)
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

#Views for adding and editing sites
@login_required(login_url='login')
def site_list(request):
    sites = Site.objects.all()
    return render(request, 'status_monitor/site_list.html', {'sites': sites})

@login_required(login_url='login')
def site_create(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('site_list'))
    else:
        form = SiteForm()
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Add Site'})

@login_required(login_url='login')
def site_edit(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            return redirect(reverse('site_list'))
    else:
        form = SiteForm(instance=site)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Edit Site'})

@login_required(login_url='login')
def site_delete(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        site.delete()
        return redirect(reverse('site_list'))
    return render(request, 'status_monitor/site_confirm_delete.html', {'site': site})

#for the status, maintenace and incidents
@login_required(login_url='login')
def status_page(request):
    sites = Site.objects.all().order_by('url')
    return render(request, "status_monitor/status_page.html", {"sites": sites})


def maintenance_page(request):
    return render(request, "status_monitor/maintenance_page.html")

def incidents_page(request):
    return render(request, "status_monitor/incidents_page.html")
