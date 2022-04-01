import re
import requests
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Avg
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from .models import UserExt, Notification, Club, ClubChat, ClubBook, ClubPost, ReadingLogBook, ProfilePost, Post, Comment, ReviewPost, PM
from .pseudomodels import Book
from .forms import register as regform, login as loginform, club as clubform, club_post as clubpostform, reading_log as readinglogform, profile_post as profilepostform, review_post as reviewpostform
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
        profile_posts = ProfilePost.objects.filter(post_profile_user = profile_user).order_by('-post_date')
        review_posts = ReviewPost.objects.filter(post_user=profile_user)
        matches = list(profile_posts) + list(review_posts)
        matches = sorted(matches, key=lambda o: o.post_date, reverse=True)
        return render(request, "readmore_app/profile.html", {'real_user': real_user, 'profile_user': profile_user, 'profile_posts': matches})
    else:
        return render(request, "readmore_app/profile.html", {'profile_user': profile_user})

def create_profile_post(request, profile_id):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        profile_user = get_object_or_404(UserExt, id=profile_id)
        form = profilepostform()
        if real_user != profile_user:
            return redirect(reverse("readmore_app:index"))
        if request.method != 'POST':
            return render(request, 'readmore_app/create_profile_post.html', {'form': form, 'profile_user': profile_user})
        else:
            form = profilepostform(request.POST)
            if form.is_valid():
                new_post = ProfilePost()
                new_post.post_profile_user = profile_user
                new_post.setup_info(real_user, form.cleaned_data['title'], form.cleaned_data['text'], form.cleaned_data['image'])
                return redirect(reverse('readmore_app:profile', kwargs={'profile_id': profile_user.id}))
            else:
                return render(request, 'readmore_app/create_profile_post.html', {'form': form, 'profile_user': profile_user})
    else:
        return redirect(reverse("readmore_app:login"))

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
        search_query = request.POST["search_query"].strip()
        results1 = UserExt.objects.filter(username__istartswith=search_query)
        results2 = UserExt.objects.filter(username__icontains=search_query)
        search_results = results1 | results2
        return render(request, "readmore_app/user_search_results.html", {"search": search_query, "user_search_results": search_results})
    else:
        raise HttpResponseNotFound()

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
        club_posts = ClubPost.objects.filter(post_club = club).order_by('-post_date')
        current_book = False
        if club.club_library.order_by('-time'):
            current_book = Book(club.club_library.order_by('-time')[0].isbn)
        return render(request, "readmore_app/club_home.html", {"real_user": real_user, "club": club, 'club_posts': club_posts, 'current_book': current_book})
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
    get_isbn13 = lambda ls: [x['identifier'] for i, x in enumerate(ls) if x['type'] == 'ISBN_13'][0]
    if request.user.is_authenticated:
        book_api_key = 'AIzaSyCrRXmYA10KFK9bFearnoAGZ8Suzn1aFgI'
        book_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+isbn:{book_isbn}&key={book_api_key}').json()
        real_user = get_object_or_404(UserExt, id=request.user.id)

        book = None
        if 'items' in book_info.keys():
            for match in book_info['items']:
                if book_isbn in [indID['identifier'] for indID in match['volumeInfo']['industryIdentifiers']]:
                    book = match
                    break
        reviews = []
        review_avg = None
        if book != None:
            try:
                reviews = ReviewPost.objects.filter(post_isbn=get_isbn13(book['volumeInfo']['industryIdentifiers'])).annotate(num_likes=Count('post_likes')).order_by('-num_likes')
                review_avg = ReviewPost.objects.filter(post_isbn="9781408855898").aggregate(Avg('post_rating'))['post_rating__avg']
                print(review_avg)
                print("REEEEEVIIEWIWWIWIWW AVVGGGG")
            except KeyError:
                pass

        return render(request, "readmore_app/view_book.html", {"real_user": real_user, "book": book, 'reviews': reviews, 'review_avg': review_avg})
        
    # Redirect Unknown Users
    return redirect(reverse('readmore_app:login'))

def search_book(request):
    if not request.user.is_authenticated: return redirect(reverse('readmore_app:login'))
    if request.method == "POST":
        query = request.POST['search_query']
        type = request.POST['search_type']
        
        real_user = get_object_or_404(UserExt, id=request.user.id)
        books = Book.search_googlebooks(query, type)
        books = [books[i:i+3] for i in range(0, len(books), 3)]
        return render(request, "readmore_app/search_book.html", {"real_user": real_user, "books": books, 'search': True})
    else:
        return render(request, "readmore_app/search_book.html", {'search': False})


def club_library(request, club_id):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        club = Club.objects.get(pk=club_id)
        club_library = Book.booklike_to_book(club.club_library.all())
        club_library = [club_library[i:i+3] for i in range(0, len(club_library), 3)]
        club_library_isbns = [book.isbn for book in club.club_library.all()]
        if real_user == club.club_owner:
            if request.method != "POST":
                return render(request, "readmore_app/club_library.html", {"real_user": real_user, "club": club, "club_library": club_library, "search": False, "club_library_isbns": club_library_isbns})
            else:
                query = request.POST['search_query']
                type = request.POST['search_type']
                
                books = Book.search_googlebooks(query, type)
                books = [books[i:i+3] for i in range(0, len(books), 3)]
                
                return render(request, "readmore_app/club_library.html", {"real_user": real_user, "club": club, "club_library": club_library, "club_library_isbns": club_library_isbns, "books": books, 'search': True})
        else:
            return render(request, "readmore_app/club_library_member_view.html", {"real_user": real_user, "club": club, "club_library": club_library, "club_library_isbns": club_library_isbns})
    else:
        return redirect(reverse("readmore_app:login"))

def create_club_post(request, club_id):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        club = Club.objects.get(pk=club_id)
        form = clubpostform()
        if real_user not in club.club_users.all():
            return redirect(reverse("readmore_app:index"))
        if request.method != 'POST':
            return render(request, 'readmore_app/create_club_post.html', {'form': form, 'club': club})
        else:
            form = clubpostform(request.POST)
            if form.is_valid():
                new_post = ClubPost()
                new_post.post_club = club
                new_post.setup_info(real_user, form.cleaned_data['title'], form.cleaned_data['text'], form.cleaned_data['image'])
                return redirect(reverse('readmore_app:club', kwargs={'club_id': club.club_id}))
            else:
                return render(request, 'readmore_app/create_club_post.html', {'form': form, 'club': club})
    else:
        return redirect(reverse("readmore_app:login"))

def reading_log(request):
    """
    The page for a user's reading log
    """
    
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        reading_log = Book.booklike_to_book(real_user.user_reading_log.all())
        reading_log = [reading_log[i:i+3] for i in range(0, len(reading_log), 3)]
        reading_log_isbns = real_user.reading_log_isbns()
        
        # Display the Reading Log Table & Search Bar
        if request.method != "POST":
            return render(request, "readmore_app/reading_log.html", {"real_user": real_user, "reading_log": reading_log, "search": False})
            
        # Display the Reading Log Table & Search Bar w/ Search Results
        else:
            query = request.POST['search_query']
            type = request.POST['search_type']
            
            books = Book.search_googlebooks(query, type)
            books = [books[i:i+3] for i in range(0, len(books), 3)]
            
            return render(request, "readmore_app/reading_log.html", {"real_user": real_user, "reading_log": reading_log, "reading_log_isbns": reading_log_isbns, "books": books, 'search': True})
    
    # Redirect Unknown Users
    return HttpResponseRedirect(reverse("readmore_app:login"))

def view_post(request, post_id, highlight=None):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        post = None
        comment = False
        try:
            post = ClubPost.objects.get(pk=post_id)
        except:
            try:
                post = ProfilePost.objects.get(pk=post_id)
            except:
                try:
                    post = ReviewPost.objects.get(pk=post_id)
                except:
                    try:
                        comment = Comment.objects.get(pk=post_id)
                        post = comment.post_parent
                        return redirect(reverse('readmore_app:view_post_highlighted_comment', kwargs={'post_id': post.post_id, 'highlight': comment.post_id}))
                    except:
                        raise Http404()
        return render(request, "readmore_app/view_post.html", {'real_user': real_user, 'post': post, 'highlight': highlight})
    else:
        return redirect(reverse("readmore_app:login"))
        
def messages(request, friend_id=None):
    get_identifier = lambda user1, user2: str(min(user1.id, user2.id)) + '_' + str(max(user1.id, user2.id))
    if not request.user.is_authenticated:
        return redirect(reverse("readmore_app:login"))
    real_user = UserExt.objects.get(pk=request.user.id)
    if friend_id is None:
        if not real_user.user_friends.count():
            return render(request, 'readmore_app/messages.html', {'real_user': real_user})
        friend_id = real_user.user_friends.order_by('username')[0].id
        return redirect(reverse('readmore_app:messages', kwargs={'friend_id': friend_id}))
    friend = get_object_or_404(UserExt, id=friend_id)
    if request.method == "POST":
        new_message = PM()
        new_message.chat_user = real_user
        new_message.chat_type = 'PM'
        new_message.chat_message = request.POST['message_text']
        new_message.chat_pm_identifier = get_identifier(real_user, friend)
        new_message.save()
        if not Notification.objects.filter(notification_user=friend, notification_type=f"{real_user.username}_pm").count():
            notify_pm = Notification()
            notify_pm.notification_type = f"{real_user.username}_pm"
            notify_pm.notification_user = friend
            notify_pm.notification_title = f"New Message From {real_user.username}"
            notify_pm.notification_link = f"/readmore/messages/{real_user.id}/"
            notify_pm.notification_link_text = f"Messages with {real_user.username}"
            notify_pm.notification_message = f"{real_user.username} has sent you a new message.  Click the link above to see."
            notify_pm.save()
    pm_list = PM.objects.filter(chat_pm_identifier=get_identifier(real_user, friend)).order_by('chat_time')
    sorted_friends = real_user.user_friends.order_by('username')
    return render(request, 'readmore_app/messages.html', {'real_user': real_user, 'friend': friend, 'pm_list': pm_list, 'sorted_friends': sorted_friends})



def create_review_post(request, book_isbn):
    if request.user.is_authenticated:
        real_user = UserExt.objects.get(pk=request.user.id)
        review_book = Book(book_isbn)
        if not review_book.title: # Checking if Google Books API returned data for the book
            raise Http404("Book Cannot Be Found")
        form = reviewpostform()
        if request.method != 'POST':
            return render(request, 'readmore_app/review_book.html', {'form': form, 'book': review_book})
        else:
            form = reviewpostform(request.POST)
            if form.is_valid():
                new_post = ReviewPost()
                new_post.post_user = real_user
                new_post.post_title = f"Review of {review_book.title}"
                new_post.post_text = form.cleaned_data['review_text']
                new_post.post_img = review_book.thumbnail
                new_post.post_isbn = review_book.isbn
                new_post.post_rating = int(form.cleaned_data['rating'])
                new_post.save()
                return redirect(reverse('readmore_app:profile', kwargs={'profile_id': real_user.id}))
            else:
                return render(request, 'readmore_app/review_book.html', {'form': form, 'book': review_book})
    else:
        return redirect(reverse("readmore_app:login"))





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

def add_to_library(request, club_id, isbn):
    if Book(isbn).book_data:
        real_user = UserExt.objects.get(pk=request.user.id)
        club = Club.objects.get(pk=club_id)
        if isbn in [obj.isbn for obj in club.club_library.all()]:
            return HttpResponse("")
        if real_user == club.club_owner:
            new_club_book = ClubBook()
            new_club_book.isbn = isbn
            new_club_book.save()
            club.club_library.add(new_club_book)
            club.save()
            book = Book.booklike_to_book(new_club_book)
            template = f"""
           <td id="clubbook{book.id}"  class="book_card">
            <a class="book_search_link" href="/readmore/view_book/{book.isbn13}">
                <div style="width: 20em;margin-left: 4%;">
                <div class="book_title">
                    <div style="width: 40%; margin: 3px;"><img width="100px" height="140px" src="{book.small_thumbnail}" alt="{book.title} Cover Image" /></div>
                    <div style="width: 100%; margin-left: 0.6em;">                   
                    <p style="font-size:18px;">{book.title}</p>
                    </div>
                </div>
                <div style="margin-top: 60%;margin-bottom: 20px;margin-left: 30px;">
                    <div style="display:flex;">
                        <div style="font-size:12px; width: 28%; margin-top: 12px;">
                            Author{'s' if len(book.authors) > 1 else ''}
                        </div>
                        <div style="width: 50%;">
                            <p style="font-size:12px;">
                                {''.join('<p style="font-size:12px;"><span style="font-size:12px;">'+author+'</span></p>' for author in book.authors)}
                            </p>
                        </div>
                    </div>
                </div>
                <div style="margin-left: 30px;">
                    <div colspan=2 style="font-size:12px;">ISBN: {book.isbn13}</div>
                </div>
            </div>
           </a>
           <div style="display: flex; flex-direction: column; justify-content: center; margin-bottom: 15px;">
            <div><div align="center"><div class="stars" style="--rating:{book.rating};margin-bottom:5%;"></div></div></div>
           <button onclick="removeBook({new_club_book.id});" class="book_action">Remove From Club Library</button>
           </div>
           </td>
            """
            return HttpResponse(template)
    return HttpResponse("error")

def remove_from_library(request, club_id, club_book_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    club = Club.objects.get(pk=club_id)
    if real_user == club.club_owner:
        club_book = ClubBook.objects.get(pk=club_book_id)
        isbn = club_book.isbn
        club.club_library.remove(club_book)
        club.save()
        club_book.delete()
        return HttpResponse(isbn)
    return HttpResponse("error")

def do_like(request, post_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    post = Post.objects.get(pk=post_id)
    if real_user in post.post_likes.all():
        post.post_likes.remove(real_user)
        post.save()
        return HttpResponse(f"unlike {post.post_likes.count()}")
    else:
        post.post_likes.add(real_user)
        post.save()
        return HttpResponse(f"like {post.post_likes.count()}")

@csrf_exempt
def make_comment(request, post_id):

    #escapeHtml = lambda unsafe: unsafe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#039;");
    real_user = UserExt.objects.get(pk=request.user.id)
    post = Post.objects.get(pk=post_id)
    data = json.loads(request.body)
    new_comment = Comment()
    new_comment.post_parent = post
    new_comment.setup_info(info_user=real_user, info_text=data['comment_text'])
    new_comment.save()
    return HttpResponse(f"""<div class="clubpost">
        <span style="position: absolute; margin-left: 95%;">
            <span id="nlikes{new_comment.post_id}">{new_comment.post_likes.count()}</span>
            <input id="likeimage{new_comment.post_id}" onclick="doLike({new_comment.post_id});" style="width: 20px;" type="image" src="{'/static/readmore_app/thumbs_up.png' if real_user in new_comment.post_likes.all() else '/static/readmore_app/thumbs_up_gray.png'}" />
        </span>
        <table style="width: 93%;">
            <tr>
                <td class="comment_by">{new_comment.post_user}<br><span style="font-size: 10px;">{datetime.now().strftime("%m/%d/%Y %I:%M %p")}</span></td>
                <td class="comment_text">{new_comment.post_text}</td>
            </tr>
        </table>
        </div>""")
        
def add_to_user_library(request, isbn):
    if Book(isbn).book_data:
        real_user = UserExt.objects.get(pk=request.user.id)
        if isbn in real_user.reading_log_isbns():
            return HttpResponse("")
        new_reading_log_book = ReadingLogBook()
        new_reading_log_book.isbn = isbn
        new_reading_log_book.save()
        real_user.user_reading_log.add(new_reading_log_book)
        real_user.save()
        book = Book.booklike_to_book(new_reading_log_book)
        template = f"""
       <td id="reading_log_book{book.id}"  class="book_card">
            <a class="book_search_link" href="/readmore/view_book/{book.isbn13}">
                <div style="width: 20em;" class="libbookind">
                <div class="book_title">
                    <div style="width: 40%; margin:3px;"><img width="100px" height="140px" src="{book.small_thumbnail}" alt="{book.title} Cover Image" /></div>
                    <div style="width: 100%; margin-left: 0.6em;">
                    
                    <p style="font-size:18px;">{book.title}</p>
                    
                    </div>
                </div>
                <div style="margin-top: 50%;margin-bottom: 20px;margin-left: 30px;">
                    <div style="display:flex;">
                        <div style="font-size:12px; width: 28%; margin-top: 12px;">
                            Author{'s' if len(book.authors) > 1 else ''}
                        </div>
                        <div style="width: 50%;">
                                {''.join('<p style="font-size:12px;"><span style="font-size:12px;">'+author+'</span></p>' for author in book.authors)}
                        </div>
                    </div>
                </div>
            </div>
            </a>
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
               <a href="/readmore/review_book/{book.isbn13}" style="display: block; margin-right: 20px;"><button class="book_action">Review Book</button></a>
               <button onclick="delete_user_library_book('{{ book.id }}');" class="book_action" style="display: block; margin-left: 20px;">Delete Book</button>
            </div>
        </td>
        """
        return HttpResponse(template)
    return HttpResponse("error")

def remove_from_user_library(request, book_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    book = ReadingLogBook.objects.get(pk=book_id)
    real_user.user_reading_log.remove(book)
    book.delete()
    return HttpResponse(book.isbn)

def delete_post(request, post_id):
    real_user = UserExt.objects.get(pk=request.user.id)
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return HttpResponse("DENY")
    if post.post_user == real_user:
        post.delete()
        return HttpResponse("CONFIRM")
    else:
        return HttpResponse("DENY")
