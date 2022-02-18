import re
import requests
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import UserExt, Notification, Club, ClubChat
from .forms import register as regform, login as loginform, club as clubform
from django.contrib.auth import authenticate, login as log_in, logout as log_out

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

def notifications(request):
    notifications = Notification.objects.filter(notification_user = UserExt.objects.get(pk=request.user.id)).order_by('-notification_time')
    return render(request, "readmore_app/notifications.html", {"notifications": notifications, 'luser': UserExt.objects.get(pk=request.user.id)})

def index(request):
    # If the user isn't logged in, redirect to login page
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("readmore_app:login"))
    return render(request, "readmore_app/index.html", {})

def login(request, account_created=None):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("readmore_app:index"))
    form = loginform()
    if request.method == 'POST':
        form = loginform(request.POST)
        if form.is_valid():
            cased_username = UserExt.objects.get(username__iexact=form.cleaned_data['username'])
            if not authenticate(username=cased_username, password=form.cleaned_data['password']):
                return render(request, "readmore_app/login.html", {'form': form, 'optional_message': "Invalid login information."})
            else:
                log_in(request, authenticate(username=cased_username, password=form.cleaned_data['password']))
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
            new_user.email = form.cleaned_data['email'].lower()
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

def user_search_results(request):
    if request.method == 'POST':
        search_query = request.POST["search_query"]
        results1 = UserExt.objects.filter(username__istartswith=search_query)
        results2 = UserExt.objects.filter(username__icontains=search_query)
        search_results = results1 | results2
        return render(request, "readmore_app/user_search_results.html", {"search": search_query, "user_search_results": search_results})
    else:
        raise Http404()

def book_clubs(request):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        book_club_list = Club.objects.filter(club_users__in=[real_user])
        return render(request, "readmore_app/book_clubs.html", {"real_user": real_user, "book_club_list": book_club_list})
    else:
        return redirect(reverse('readmore_app:login'))
    
def club(request, club_id):
    """
    The home page for book clubs
    """
    if request.user.is_authenticated:
        club = get_object_or_404(Club, club_id=club_id)
        real_user = get_object_or_404(UserExt, id=request.user.id)
        return render(request, "readmore_app/club_home.html", {"real_user": real_user, "club": club})
    else:
        return redirect(reverse('readmore_app:login'))

def club_members(request, club_id):
    if request.user.is_authenticated:
        club = get_object_or_404(Club, club_id=club_id)
        real_user = get_object_or_404(UserExt, id=request.user.id)
        return render(request, "readmore_app/club_members_list.html", {"real_user": real_user, "club": club})
    else:
        return redirect(reverse('readmore_app:login'))

def invite_to_club(request, club_id):
    if request.user.is_authenticated:
        club = get_object_or_404(Club, club_id=club_id)
        real_user = get_object_or_404(UserExt, id=request.user.id)
        if club.club_owner != real_user:
            return redirect(reverse('readmore_app:club', kwargs={'club_id': club.club_id}))
        return render(request, "readmore_app/invite_to_club.html", {"real_user": real_user, "club": club})
    else:
        return redirect(reverse('readmore_app:login'))

def club_chat(request, club_id):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        club = Club.objects.get(pk=club_id)
        if real_user not in club.club_users.all():
            return redirect(reverse('readmore_app:index'))
        club_chats = ClubChat.objects.filter(chat_destination=club).order_by('chat_time')
        return render(request, "readmore_app/club_chat.html", {"real_user": real_user, "club": club, 'club_chats': club_chats})
    else:
        return redirect(reverse('readmore_app:login'))

def view_book(request, book_isbn):
    """
    The page for viewing books
    """
    
    if request.user.is_authenticated:
        book_api_key = 'AIzaSyCrRXmYA10KFK9bFearnoAGZ8Suzn1aFgI'
        book_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+isbn:{book_isbn}&key={book_api_key}').json()
        real_user = get_object_or_404(UserExt, id=request.user.id)

        book = None
        if 'items' in book_info.keys():
            book = book_info['items'][0]

        return render(request, "readmore_app/view_book.html", {"real_user": real_user, "book": book})
        
    # Redirect Unknown Users
    return redirect(reverse('readmore_app:login'))

def search_book(request):
    if not request.user.is_authenticated: return redirect(reverse('readmore_app:login'))
    if request.method == "POST":
        query = request.POST['search_query']
        type = request.POST['search_type']
        
        book_api_key = 'AIzaSyCrRXmYA10KFK9bFearnoAGZ8Suzn1aFgI'
        real_user = get_object_or_404(UserExt, id=request.user.id)
        
        if type == "general":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&key={book_api_key}').json()
        elif type == "title":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+intitle:{query}&maxResults=40&key={book_api_key}').json()
        elif type == "author":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+inauthor:{query}&maxResults=40&key={book_api_key}').json()
        elif type == "isbn":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+isbn:{query}&maxResults=40&key={book_api_key}').json()

        if 'items' in books_info.keys():
            books = books_info['items']
        else:
            books = []
        
        books = [books[i:i+3] for i in range(0, len(books), 3)]
        
        return render(request, "readmore_app/search_book.html", {"real_user": real_user, "books": books, 'search': True})
    else:
        return render(request, "readmore_app/search_book.html", {'search': False})

""" 
*************************************
* AJAX METHODS ONLY AFTER THIS POINT 
*************************************
"""

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

def leave_club(request, club_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    club = Club.objects.get(pk=club_id)
    if club.club_owner == real_user:
        club_users = club.club_users.all()
        for member in club_users:
            if member != real_user:
                notify_member = Notification()
                notify_member.notification_user = member
                notify_member.notification_title = "A Book Club You Are a Member of Has Been Deleted"
                notify_member.notification_message = f"The owner of the book club {club.club_name} has deleted this book club."
                notify_member.save()
        club.delete()
        return HttpResponse("")
    else:
        club.club_users.remove(real_user)
        club.save()
        notify_owner = Notification()
        notify_owner.notification_user = club.club_owner
        notify_owner.notification_title = f"{real_user.username} Has Left Your Book Club"
        notify_owner.notification_link = f'/readmore/club/{club.club_id}'
        notify_owner.notification_link_text = club.club_name
        notify_owner.notification_message = f"{real_user.username} has left your book club, {club.club_name}."
        notify_owner.save()
        return HttpResponse("")

def delete_notification(request, notification_id):
    Notification.objects.filter(notification_id=notification_id).delete()
    return HttpResponse("")

def get_friend_count(request, user_id):
    this_user = get_object_or_404(UserExt, id=user_id)
    num_friends = this_user.user_friends.all().count()
    return HttpResponse(str(num_friends))

def kick_member(request, club_id, member_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    club = Club.objects.get(pk=club_id)
    member = UserExt.objects.get(pk=member_id)
    if club.club_owner == real_user:
        club.club_users.remove(member)
        club.save()
        notify_member = Notification()
        notify_member.notification_user = member
        notify_member.notification_title = "You Have Been Kicked From A Book Club"
        notify_member.notification_message = f"The owner of the book club {club.club_name} has kicked you from this book club."
        notify_member.save()
    return HttpResponse("")

def invite_member(request, club_id, friend_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    club = Club.objects.get(pk=club_id)
    member = UserExt.objects.get(pk=friend_id)
    if club.club_owner == real_user:
        club.club_pending_invites.add(member)
        notify_member = Notification()
        notify_member.notification_user = member
        notify_member.notification_title = "You Have Been Invited To A Book Club"
        notify_member.notification_message = f"You have been invited to the book club {club.club_name} by {real_user.username}.  To accept the invitation, click the above link to the book club's homepage and click the 'Join' button."
        notify_member.notification_link = f"/readmore/club/{club.club_id}/"
        notify_member.notification_link_text = club.club_name
        notify_member.save()
    return HttpResponse("")

def join_club(request, club_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    club = Club.objects.get(pk=club_id)
    if real_user in club.club_pending_invites.all():
        club.club_pending_invites.remove(real_user)
        club.club_users.add(real_user)
        club.save()
        notify_owner = Notification()
        notify_owner.notification_user = club.club_owner
        notify_owner.notification_title = f"{real_user.username} Has Joined Your Book Club"
        notify_owner.notification_link = f'/readmore/club/{club.club_id}'
        notify_owner.notification_link_text = club.club_name
        notify_owner.notification_message = f"{real_user.username} has joined your book club, {club.club_name}."
        notify_owner.save()
    return HttpResponse("")