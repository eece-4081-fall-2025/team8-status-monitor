from django import forms
from .models import MonitoredSite

class MonitoredSiteForm(forms.ModelForm):
    class Meta:
        model = MonitoredSite
        fields = ['name', 'url', 'check_frequency']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_url(self):
        url = self.cleaned_data['url']
        qs = MonitoredSite.objects.filter(url=url, user=self.user)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("You are already monitoring this site.")
        return url
    
    def clean_name(self):
        name= self.cleaned_data.get('name', '')
        return name.title()
