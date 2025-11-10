from django.db import models
from django.contrib.auth.models import User # REQUIRED for UserProfile
from django.db.models.signals import post_save # REQUIRED for signals
from django.dispatch import receiver # REQUIRED for signals

class Site(models.Model):
    STATUS_CHOICES = [
        ('UP', 'UP'),
        ('DOWN', 'DOWN'),
    ]
    
    # --- Epic 1: Category Field ---
    CATEGORY_CHOICES = [
        ('CRIT', 'Critical'),
        ('APP', 'Application'),
        ('WEB', 'Public Website'),
        ('DB', 'Database'),
        ('OTHER', 'Other'),
    ]
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='WEB'
    )
    # -----------------------------

    name = models.CharField(max_length=100)
    url = models.URLField(unique =True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True,blank = True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UP')
    response_ime = models.FloatField(default=0.0) #in seconds 
    
    def __str__(self):
        return self.name

# --- Permission Control: New UserProfile Model ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Default=True means a new user can configure sites
    can_configure_sites = models.BooleanField(default=True) 

    def __str__(self):
        return self.user.username + " Profile"
    
# Signals to automatically create a UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, can_configure_sites=True)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()