from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import UserExt
import re
from datetime import date, timedelta, datetime

class club_post(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'size':50}), validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid post title less than 100 characters must be provided.")])
    image = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':50}))
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)

class profile_post(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'size':50}), validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid post title must be provided.")])
    image = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':50}))
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)


class login(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'maxlength': "50"}))
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
    password = forms.CharField(widget = forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget = forms.PasswordInput(), required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserExt.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already in use.")
        if not username or not re.match("^[a-zA-Z_\-0-9]+[a-zA-Z_\-0-9]*$", username):
            raise ValidationError("A valid username must be provided.")
        if len(username) > 50:
            raise ValidationError("Username must be less than or equal to 50 characters.")
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserExt.objects.filter(email=email.lower()).exists():
            raise ValidationError("Email already in use.")
        else:
            return email
    
    def clean_birthdate(self):
        birthdate = self.cleaned_data['birthdate']
        if type(birthdate) is type(None):
            raise ValidationError("Birthdate must be entered in the form MM/DD/YYYY.")
        elif birthdate > date.today() - timedelta(days=1095) or birthdate < date(1900, 1, 1):
            raise ValidationError("A valid birthdate must be provided.")
        else:
            return birthdate
    
    # this really should be clean_password but this validation requires two fields
    def clean(self):
        cleaned_data=super().clean()
        password = cleaned_data.get('password') or ""
        print(password)
        confirm_password = cleaned_data.get('confirm_password') or ""
        if not re.match("^[^\s]{8}[^\s]*$", password):
            raise ValidationError("Password must be 8 characters or more in length")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        else:
            return cleaned_data


class club(forms.Form):
	name = forms.CharField(validators=[validators.RegexValidator(regex="^[a-zA-Z_\-0-9].{2,99}$", message="A valid book club name must be provided.")])
	description = forms.CharField(validators=[validators.RegexValidator("^[a-zA-Z_\-0-9].{0,300}$", message="Description must be 300 or fewer characters.")], widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;', 'min-height': '50px'}), required=False)


class reading_log(forms.Form):
	isbn = forms.CharField(validators=[validators.RegexValidator(regex="^(?=(?:[0-9]){10}(?:(?:[0-9]){3})?$)[0-9]+$", message="Invalid entry for ISBN.")])


class review_post(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'style': 'resize: vertical;'}), required=False)
    rating = forms.ChoiceField(choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)))

class meeting(forms.Form):
    meeting_name = forms.CharField(widget=forms.TextInput(attrs={'size':50}), validators=[validators.RegexValidator(regex="^.{0,100}$", message="Meeting name must be less than 100 characters.")], required=False)
    meeting_date = forms.DateField(widget=forms.SelectDateWidget(years=[*range(datetime.now().year, datetime.now().year + 100)]))
    meeting_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    meeting_description = forms.CharField(validators=[validators.RegexValidator(".{0,300}$", message="Description must be 300 or fewer characters.")], widget=forms.Textarea(attrs={'cols': 50, 'rows': 6, 'style': 'resize: vertical;'}), required=False)
    
    def clean(self):
        cleaned_data=super().clean()
        try:
            meeting_date = cleaned_data['meeting_date']
        except:
            return ValidationError("Date does not exist.")
        meeting_time = cleaned_data['meeting_time']
        meeting_datetime = datetime.combine(meeting_date, meeting_time)
        if meeting_datetime < datetime.now():
            raise ValidationError("Meeting must not be in the past")
        return cleaned_data