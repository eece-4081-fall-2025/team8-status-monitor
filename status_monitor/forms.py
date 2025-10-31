from django import forms
from .models import Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name','url','description','is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            }