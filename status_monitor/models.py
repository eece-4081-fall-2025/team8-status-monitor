from django.db import models
from django.contrib.auth.models import User
class Site(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique =True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True,blank = True)

    #added dashboard fields
    status = models.CharField(max_length=10, choices=[('UP', 'UP'), ('DOWN', 'DOWN')], default='UP')
    response_ime = models.FloatField(default=0.0) #in seconds
    def __str__(self):
        return self.name
    
class MonitoredSite(models.Model):
    name = models.CharField(max_length = 100)
    url = models.URLField(unique = True)
    check_frequency = models.IntegerField(default = 5,help_text="Frequency (in minutes) to check site status")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'monitored_sites')
    
    def __str__(self):
        return self.name