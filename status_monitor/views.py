from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from datetime import timedelta
from .models import  MonitoredSite
from .models import UserProfile
from .forms import MonitoredSiteForm

# --- New Decorator to Enforce Configuration Permission ---
def configuration_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Auto-create profile safely
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.can_configure_sites:
            messages.error(request, "You do not have permission to configure sites.")
            return redirect('status_page')

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
# -------------------------------------------------------

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

@login_required(login_url='login')
def site_list(request):
    sites = MonitoredSite.objects.filter(user=request.user)
    return render(request, 'status_monitor/site_list.html', {'sites': sites})

@configuration_required  # NEW DECORATOR APPLIED
def site_create(request):
    if request.method == 'POST':
        form = MonitoredSiteForm(request.POST, user=request.user)
        # Handle duplicate URLs gracefully: redirect instead of re-rendering form
        if not form.is_valid():
            if "You are already monitoring this site." in str(form.errors):
                messages.info(request, "You are already monitoring this site.")
                return redirect(reverse('status_page'))
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            messages.success(request, "Site added successfully!")
            return redirect(reverse('status_page'))
    else:
        form = MonitoredSiteForm(user=request.user)
    return render(request, 'status_monitor/site_form.html', {'form': form, 'title': 'Add Site'})

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

@configuration_required # NEW DECORATOR APPLIED
def site_delete(request, pk):
    site = get_object_or_404(MonitoredSite, pk=pk, user=request.user)
    if request.method == 'POST':
        site.delete()
        return redirect(reverse('status_page'))
    return render(request, 'status_monitor/site_confirm_delete.html', {'site': site})

@login_required(login_url='login')
def status_page(request):
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
