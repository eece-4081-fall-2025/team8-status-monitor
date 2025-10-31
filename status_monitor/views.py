from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

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
    return render(request, 'status_monitor/home.html')