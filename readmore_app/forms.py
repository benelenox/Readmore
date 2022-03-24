from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import UserExt
import re
from datetime import date, timedelta, datetime

class club_post(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'size':50}), validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid post title must be provided.")])
    image = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':50}))
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)

class profile_post(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'size':50}), validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid post title must be provided.")])
    image = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':50}))
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)


class login(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    def clean_username(self):
        username = self.cleaned_data['username']
        if not UserExt.objects.filter(username__iexact=username).exists():
            raise ValidationError(f"{username} is not a valid user.")
        else:
            return username


class register(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z -]+$", message="Invalid entry for first name.")])
    last_name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z -]+$", message="Invalid entry for last name.")])
    email = forms.EmailField(validators=[validators.EmailValidator(message="A valid email must be provided.")])
    birthdate = forms.DateField(widget=forms.SelectDateWidget(years=[*range(1900, datetime.now().year)]))
    password = forms.CharField(widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserExt.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already in use.")
        if not username or not re.match("^[a-zA-Z_\-0-9]+[a-zA-Z_\-0-9]*$", username):
            raise ValidationError("A valid username must be provided.")
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserExt.objects.filter(email=email.lower()).exists():
            raise ValidationError("Email already in use.")
        else:
            return email

    # this really should be clean_password but this validation requires two fields
    def clean(self):
        cleaned_data=super().clean()
        birthdate = self.cleaned_data['birthdate']
        if type(birthdate) is type(None):
            raise ValidationError("Birthdate must be entered in the form MM/DD/YYYY.")
        elif birthdate > date.today() - timedelta(days=1095) or birthdate < date(1900, 1, 1):
            raise ValidationError("A valid birthdate must be provided.")
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if not re.match("^[^ ]{8}[^ ]*$", password):
            raise ValidationError("Password must be 8 characters or more in length")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        else:
            return cleaned_data


class club(forms.Form):
	name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid book club name must be provided.")])
	description = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)


class reading_log(forms.Form):
	isbn = forms.CharField(validators=[validators.RegexValidator(regex="^(?=(?:[0-9]){10}(?:(?:[0-9]){3})?$)[0-9]+$", message="Invalid entry for ISBN.")])


class review_post(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)
    rating = forms.ChoiceField(choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)))