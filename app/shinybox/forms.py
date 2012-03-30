from django import forms
from django.contrib.auth.models import User
from models import *

class StartForm(forms.Form):
    domain = forms.CharField(max_length=256)
    email  = forms.EmailField(label="Your Email")
    password = forms.CharField( widget=forms.PasswordInput, label="Password" )
    #confirm = forms.CharField( widget=forms.PasswordInput, label="Password confirm" )
    
    def clean_email(self):
        data=self.cleaned_data['email']
        try:
            User.objects.get(email=data)
            raise forms.ValidationError('An account with that email already exists.')
        except User.DoesNotExist:
            return data
            

class FileForm(forms.ModelForm):
    class Meta:
        model = File