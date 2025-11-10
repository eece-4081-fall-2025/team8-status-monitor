from django import forms
from .models import Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        # Ensure 'category' is here
        fields = ['name','url','description','category','is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            }