from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

def home(request):
    return render(request, 'home.html')


#Begin user registration and authentication views
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboard'))
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse('dashboard'))
    else:
        form = UserCreationForm()
        
    return render(request, 'todo/register.html', {'form': form, 'title': 'Create Account'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboard'))
    
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
            return redirect(reverse('dashboard'))
        else:
            context['error'] = "Invalid username or password."
        
    context.setdefault('next', next_url)
    return render(request, 'todo/login.html', context)
        
def logout_view(request):
    if request.method == 'GET':
        return render(request, 'todo/logout_confirm.html')
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have been logged out.")
        return redirect(reverse('home'))

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'todo/dashboard.html', {'title': 'Dashboard'})