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
    
    def get_recent_checks(self,limit=20):
        return self.check_results.order_by('-timestamp')[:limit][::-1]
    
    def calculate_uptime(self):
        total=self.check_results.count()
        if total == 0:
            return 0.0
        up_count = self.check_results.filter(is_up=True).count()
        return round(up_count / total * 100,2)
    

    def get_status_summary(self, limit=20):
        checks=self.get_recent_checks(limit=limit)
        timestamps = [c.timestamp.strftime("%H:%M") for c in checks]
        response_time = [c.response_time for c in checks]
        status_points = ["Up" if c.is_up else "Down" for c in checks]
        uptime = self.calculate_uptime()

        latest_check = checks[-1] if checks else None
        return {
            'site' : self,
            'latest_check': latest_check,
            'history' : checks,
            'timestamps' : timestamps,
            'response_times' : response_time,
            'status_points' : status_points,
            'uptime' : uptime,
        }
    
class SiteCheckResult(models.Model):
    site = models.ForeignKey(MonitoredSite, on_delete=models.CASCADE, related_name='check_results')
    timestamp= models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField(null=True, blank= True)
    response_time = models.FloatField(help_text="Response time in seconds")
    is_up = models.BooleanField(default= False)
    
    def __str__(self):
        return f"{self.site.name} - {self.timestamp} - {self.status_code}"