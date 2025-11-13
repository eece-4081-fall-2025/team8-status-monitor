from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    can_configure_sites = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
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
    
    def calculate_uptime(self, checks):
        total = len(checks)
        if total == 0:
            return 0.0
        up_count = sum(1 for c in checks if c.is_up)
        return round(up_count / total * 100, 2)
    

    def get_status_summary(self, limit=20):
        checks = self.get_recent_checks(limit)

        return {
            "site": self,
            "latest_check": checks[-1] if checks else None,
            "history": list(checks),
            "timestamps": [c.timestamp.isoformat() for c in checks],
            "response_times": [
                float(c.response_time) if c.response_time is not None else None
                for c in checks
            ],
            "status_points": ["Up" if c.is_up else "Down" for c in checks],
            "uptime": self.calculate_uptime(checks),
        }
    
class SiteCheckResult(models.Model):
    site = models.ForeignKey(MonitoredSite, on_delete=models.CASCADE, related_name='check_results')
    timestamp= models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField(null=True, blank= True)
    response_time = models.FloatField(help_text="Response time in seconds")
    is_up = models.BooleanField(default= False)
    
    def __str__(self):
        return f"{self.site.name} - {self.timestamp} - {self.status_code}"


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        return

    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)