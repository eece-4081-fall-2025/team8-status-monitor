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
        #must be https
        def clean_url(self):
            url = self.cleaned_data['url']
        #preventing dup. urls
            if self.user and Site.objects.filter(url=url).exists():
                raise forms.ValidationError("This site is already being monitored")
            #basice scheme check
            parsed = urlparse(url)
            if parsed.scheme not in ('https'):
                raise forms.ValidationError("URL must start with https://")