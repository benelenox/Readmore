import re
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserExt, Notification
from .forms import register as regform, login as loginform
from django.contrib.auth import authenticate, login as log_in, logout as log_out

def delete_notification(request, notification_id):
    Notification.objects.filter(notification_id=notification_id).delete()

def notifications(request):
    notifications = Notification.objects.filter(notification_user = UserExt.objects.get(pk=request.user.id))
    return render(request, "readmore_app/notifications.html", {"notifications": notifications})

def index(request):
    # If the user isn't logged in, redirect to login page
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("readmore_app:login"))
    return render(request, "readmore_app/index.html", {})

def login(request, account_created=None):
    form = loginform()
    if request.method == 'POST':
        form = loginform(request.POST)
        if form.is_valid():
            if not authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']):
                return render(request, "readmore_app/login.html", {'form': form, 'optional_message': "Invalid login information."})
            else:
                log_in(request, authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']))
                return HttpResponseRedirect(reverse("readmore_app:index"))
    
    context = {'form': form}
    if account_created:
        context['optional_message'] = "Account has been created."
    return render(request, 'readmore_app/login.html', context)

def registration(request):
    form = regform()
    if request.method == 'POST':
        form = regform(request.POST)
        if form.is_valid():
            new_user = UserExt()
            new_user.username = form.cleaned_data['username']
            new_user.set_password(form.cleaned_data['password'])
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.email = form.cleaned_data['email']
            new_user.user_birthdate = form.cleaned_data['birthdate']
            new_user.save()
            return redirect(reverse('readmore_app:login_account_created', kwargs={'account_created':1}))
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("readmore_app:index"))
    return render(request, 'readmore_app/registration.html', {'form': form})

def logout(request):
    log_out(request)
    return HttpResponseRedirect(reverse("readmore_app:login"))