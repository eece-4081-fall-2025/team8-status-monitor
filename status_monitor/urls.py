"""
URL configuration for status_monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sites/',views.site_list, name='site_list'),
    path('sites/<int:pk>/history/', views.site_history, name='site_history'),
    path('sites/add/', views.site_create, name= 'site_create'),
    path('sites/<int:pk>/edit/', views.site_edit, name='site_edit'),
    path('sites/<int:pk>/delete/', views.site_delete, name='site_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('status/', views.status_page,name='status_page' ),
    path('maintenance/', views.maintenance_page,name='maintenance_page'),
    path('incidents/', views.incidents_page,name='incidents_page' ),
]
