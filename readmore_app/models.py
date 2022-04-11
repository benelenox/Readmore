import re
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# User model extension for adding more attributes
class UserExt(User):
    user_friends = models.ManyToManyField('UserExt', related_name="friends")
    user_birthdate = models.DateField()
    user_bio = models.TextField()
    user_pending_friends = models.ManyToManyField('UserExt', related_name="pending_friends")
    user_reading_log = models.ManyToManyField('ReadingLogBook', related_name="reading_log")
    
    def num_notifications(self):
        return Notification.objects.filter(notification_user=self).count()
        
    def reading_log_isbns(self):
        return [book.isbn for book in self.user_reading_log.all()]

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    notification_type = models.CharField(max_length=10000, blank=True)
    notification_user = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    notification_title = models.CharField(max_length=10000)
    notification_time = models.DateTimeField(auto_now_add=True)
    notification_link = models.CharField(max_length=10000, blank=True)
    notification_link_text = models.CharField(max_length=10000, blank=True)
    notification_message = models.TextField()

class Club(models.Model):
    club_id = models.AutoField(primary_key=True)
    club_name = models.CharField(max_length=100)
    club_description = models.TextField(blank=True)
    club_owner = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    club_users = models.ManyToManyField(UserExt, related_name="user_clubs")
    club_pending_invites = models.ManyToManyField('UserExt', related_name="pending_invites")
    club_library = models.ManyToManyField('ClubBook', related_name='clubs')

class ClubBook(models.Model):
    isbn = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)

class ReadingLogBook(models.Model):
    isbn = models.CharField(max_length=13)
    time = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    chat_user = models.ForeignKey(UserExt, null=True, on_delete=models.SET_NULL)
    chat_time = models.DateTimeField(auto_now_add=True)
    chat_type = models.CharField(default="chat", blank=False, null=False, max_length=20)
    chat_message = models.TextField()

class ClubChat(Chat):
    chat_destination = models.ForeignKey(Club, on_delete=models.CASCADE)

class PM(Chat):
    chat_pm_identifier = models.CharField(max_length=100)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_user = models.ForeignKey(UserExt, models.DO_NOTHING)
    post_title = models.TextField()
    post_text = models.TextField()
    post_img = models.TextField(blank=True)
    post_likes = models.ManyToManyField(UserExt, related_name="likes")
    post_date = models.DateTimeField(auto_now_add=True)
    
    def setup_info(self, info_user, info_title=None, info_text="", info_image="", info_date=datetime.now()):
        """
        Used for initializing the basic values of a Post
        """
        
        self.post_user = info_user
        self.post_title = info_title or f"Post by {self.post_user.username}"
        self.post_text = info_text
        self.post_img = info_image
        self.post_date = info_date
        
        # Escape HTML Characters in Post's Message
        self.post_text = self.post_text.replace('&', "&amp;")
        self.post_text = self.post_text.replace('<', "&lt;")
        self.post_text = self.post_text.replace('>', "&gt;")
        self.post_text = self.post_text.replace('"', "&quot;")
        self.post_text = self.post_text.replace("'", "&#39;")
        
        # Save Post
        self.save()
        
        # Tagged Users in Post's Message
        tag_list = re.findall("@[a-zA-Z_\-0-9]+", self.post_text)
        tag_user_set = set()
        for tag in tag_list:
            try:
                tag_username = tag[1:]
                tag_user = UserExt.objects.get(username=tag_username)
                
                # Link to Tagged User's Profile
                self.post_text = self.post_text.replace(tag, f'<a href="/readmore/profile/{tag_user.id}">&#64;{tag_username}</a>', 1)
                self.save()
                
                # Notify Tagged User
                if tag_user != self.post_user and tag_user not in tag_user_set:
                    tag_user_set.add(tag_user)
                    notify_tag = Notification()
                    notify_tag.notification_type = f"tag"
                    notify_tag.notification_user = tag_user
                    notify_tag.notification_title = f"You Were Tagged by {self.post_user.username}"
                    notify_tag.notification_link = f"/readmore/view_post/{self.post_id}/"
                    notify_tag.notification_link_text = f"{self.post_title}"
                    notify_tag.notification_message = f"{self.post_user.username} has tagged you in their post.  Click the link above to see."
                    notify_tag.save()
                    
            except ObjectDoesNotExist:
                pass
    
    def date_formatted(self):
        return self.post_date.strftime("%m/%d/%Y %I:%M:%S %p")
    
    def get_likes(self):
        return len(self.post_likes.all()) - len(self.post_dislikes.all())

class ClubPost(Post):
    post_club = models.ForeignKey(Club, on_delete=models.CASCADE)

class ProfilePost(Post):
    post_profile_user = models.ForeignKey(UserExt, on_delete=models.CASCADE)

class Comment(Post):
    post_parent = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

class ReviewPost(Post):
    post_isbn = models.TextField()
    post_rating = models.IntegerField()
	
class BookForumPost(Post):
    post_isbn = models.TextField()