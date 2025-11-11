from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


    
class MonitoredSite(models.Model):
    name = models.CharField(max_length = 100)
    url = models.URLField(unique = True)
    check_frequency = models.IntegerField(default = 5,help_text="Frequency (in minutes) to check site status")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'monitored_sites')

    class Meta:
        unique_together = ('user', 'url')
    def __str__(self):
        return self.name
    
class SiteCheckResult(models.Model):
    site = models.ForeignKey(MonitoredSite, on_delete=models.CASCADE, related_name='check_results')
    timestamp= models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField(null=True, blank= True)
    response_time = models.FloatField(help_text="Response time in seconds")
    is_up = models.BooleanField(default= False)
    
    def __str__(self):
        return f"{self.site.name} - {self.timestamp} - {self.status_code}"