from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import UserExt
import re
from datetime import date, timedelta

class login(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    def clean_username(self):
        username = self.cleaned_data['username']
        if not len(UserExt.objects.filter(username=username)):
            raise ValidationError(f"{username} is not a valid user.")
        else:
            return username
    
    
class register(forms.Form):
    username = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9]+.*$", message="A valid username must be provided.")])
    first_name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z -]+$", message="Invalid entry for first name.")])
    last_name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z -]+$", message="Invalid entry for last name.")])
    email = forms.EmailField(validators=[validators.EmailValidator(message="A valid email must be provided.")])
    birthdate = forms.DateField()
    password = forms.CharField(validators=[validators.RegexValidator(regex="^[^ ]{8}[^ ]*$", message="Password must be 8 characters or more in length")], widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(UserExt.objects.filter(username=username)) or not username:
            if len(UserExt.objects.filter(username=username)):
                raise ValidationError("Username already in use.")
            else:
                raise ValidationError("A valid username must be provided.")
        else:
            return username

    def clean(self):
        cleaned_data=super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        birthdate = cleaned_data.get('birthdate')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        if type(birthdate) is type(None):
            raise ValidationError("Birthdate must be entered in the form MM/DD/YYYY.")
        elif birthdate > date.today() - timedelta(days=1095) or birthdate < date(1900, 1, 1):
            raise ValidationError("A valid birthdate must be provided.")
        elif len(UserExt.objects.filter(username=username)):
            raise ValidationError("Username already in use.")
        elif not username:
            raise ValidationError("A valid username must be provided.")
        elif len(UserExt.objects.filter(email=email)):
            raise ValidationError("Email already in use.")
        else:
            return cleaned_data
			
class club(forms.Form):
	name        = forms.CharField()
	description = forms.CharField(widget=forms.Textarea)