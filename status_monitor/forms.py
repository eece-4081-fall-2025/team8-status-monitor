from django import forms
from .models import MonitoredSite

class MonitoredSiteForm(forms.ModelForm):
    class Meta:
        model = MonitoredSite
        fields = ['name', 'url', 'check_frequency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site name'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'check_frequency': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Check frequency (minutes)'}),
        }

    def clean_url(self):
        url = self.cleaned_date['url']
        if MonitoredSite.objects.filter(url=url, user=self.initial.get('user')).exists:
            raise forms.ValidationError("You are already monitoring this site.")
        return url