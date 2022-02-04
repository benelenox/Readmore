import re
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserExt, Notification, Club
from .forms import register as regform, login as loginform, club as clubform
from django.contrib.auth import authenticate, login as log_in, logout as log_out
from datetime import datetime

def friend_list(request, profile_id):
    profile_user = get_object_or_404(UserExt, id=profile_id)
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        return render(request, "readmore_app/friend_list.html", {'real_user': real_user, 'profile_user': profile_user})
    else:
        return render(request, "readmore_app/friend_list.html", {'profile_user': profile_user})

def profile(request, profile_id):
    profile_user = get_object_or_404(UserExt, id=profile_id)
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        return render(request, "readmore_app/profile.html", {'real_user': real_user, 'profile_user': profile_user})
    else:
        return render(request, "readmore_app/profile.html", {'profile_user': profile_user})

@csrf_exempt
def process_friend(request):
    if request.method == "POST":
        real_user = UserExt.objects.get(pk=request.POST['real_user_id'])
        profile_user = UserExt.objects.get(pk=request.POST['profile_user_id'])
        type = request.POST['type']
        if type == "add":
            if real_user in profile_user.user_pending_friends.all():
                profile_user.user_pending_friends.remove(real_user)
                profile_user.user_friends.add(real_user)
                profile_user.save()
                real_user.user_friends.add(profile_user)
                real_user.save()
                notify_friend_added = Notification()
                notify_friend_added.notification_type = "friend"
                notify_friend_added.notification_user = profile_user
                notify_friend_added.notification_title = "New Friend!"
                notify_friend_added.notification_link = f"/readmore/profile/{real_user.id}/"
                notify_friend_added.notification_link_text = f"@{real_user.username}"
                notify_friend_added.notification_message = f"{real_user.username} has accepted your friend request!"
                notify_friend_added.save()
                return HttpResponse("added")
            else:
                real_user.user_pending_friends.add(profile_user)
                real_user.save()
                notify_friend_request = Notification()
                notify_friend_request.notification_type = "friend"
                notify_friend_request.notification_user = profile_user
                notify_friend_request.notification_title = f"Friend Request"
                notify_friend_request.notification_link = f"/readmore/profile/{real_user.id}/"
                notify_friend_request.notification_link_text = f"@{real_user.username}"
                notify_friend_request.notification_message = f"{real_user.username} wants to be your friend.  Go to their profile and click the add friend button to add them."
                notify_friend_request.save()
                return HttpResponse('pending')
        elif type == "pending":
            real_user.user_pending_friends.remove(profile_user)
            real_user.save()
            return HttpResponse("")
        elif type == "remove":
            profile_user.user_friends.remove(real_user)
            real_user.user_friends.remove(profile_user)
            return HttpResponse("")

def get_friend_count(request, user_id):
    this_user = get_object_or_404(UserExt, id=user_id)
    num_friends = this_user.user_friends.all().count()
    return HttpResponse(str(num_friends))
    
def delete_notification(request, notification_id):
    Notification.objects.filter(notification_id=notification_id).delete()

def notifications(request):
    notifications = Notification.objects.filter(notification_user = UserExt.objects.get(pk=request.user.id))
    return render(request, "readmore_app/notifications.html", {"notifications": notifications, 'luser': UserExt.objects.get(pk=request.user.id)})

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

def create_club(request):
    """
    The creation page for book clubs
    """
    
    if request.user.is_authenticated:
        form = clubform()
        
        # Create a Book Club
        if request.method == 'POST':
            form = clubform(request.POST)
            
            if form.is_valid():
                new_club = Club()
                
                new_club.club_name = form.cleaned_data['name']
                new_club.club_description = form.cleaned_data['description']
                new_club.club_owner = UserExt.objects.get(pk=request.user.id)
                new_club.save()
                new_club.club_users.add(new_club.club_owner)
                new_club.save()
                
                
                return redirect(reverse('readmore_app:club', kwargs={ 'club_id': new_club.club_id }))
                
        # Display the Book Club Creation Form
        return render(request, "readmore_app/create_club.html", { 'form': form })
    
    # Redirect Unknown Users
    return HttpResponseRedirect(reverse("readmore_app:login"))
    
def club(request, club_id=None):
    """
    The home page for book clubs
    """
    
    return index(request) # Temporary