from django.shortcuts import render, redirect
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