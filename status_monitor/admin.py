from django.contrib import admin
from .models import MonitoredSite

@admin.register(MonitoredSite)
class MonitoredSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'check_frequency', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'url')