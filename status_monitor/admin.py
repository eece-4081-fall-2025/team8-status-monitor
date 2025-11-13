from django.contrib import admin
from .models import Site

class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'status', 'category', 'is_active', 'last_checked')
    list_filter = ('status', 'category', 'is_active')
    search_fields = ('name', 'url')
    readonly_fields = ('last_checked', 'status', 'response_time')

admin.site.register(Site, SiteAdmin)