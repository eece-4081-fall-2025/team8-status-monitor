from django.db import models

class Site(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique =True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True,blank = True)
    
    def __str__(self):
        return self.name