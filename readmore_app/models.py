from django.db import models
from django.contrib.auth.models import User

# User model extension for adding more attributes
class UserExt(User):
    user_friends = models.ManyToManyField('UserExt', related_name="friends")
    user_birthdate = models.DateField()
    user_bio = models.TextField()
    user_pending_friends = models.ManyToManyField('UserExt', related_name="pending_friends")
    
    def num_notifications(self):
        return Notification.objects.filter(notification_user=self).count()


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    notification_type = models.CharField(max_length=10000, blank=True)
    notification_user = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    notification_title = models.CharField(max_length=10000)
    notification_time = models.DateTimeField(auto_now_add=True)
    notification_link = models.CharField(max_length=10000, blank=True)
    notification_link_text = models.CharField(max_length=10000, blank=True)
    notification_message = models.TextField()

class Book(models.Model):
    book_isbn = models.CharField(max_length=1000, primary_key=True)
    book_title = models.CharField(max_length=1000)
    book_genre = models.CharField(max_length=1000)
    book_bookcover_picture_link = models.CharField(max_length=1000)

class Club(models.Model):
    club_id = models.AutoField(primary_key=True)
    club_name = models.CharField(max_length=100)
    club_description = models.TextField(blank=True)
    club_owner = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    club_users = models.ManyToManyField(UserExt, related_name="users")
    club_library = models.ManyToManyField('Book', blank=True, related_name="library")
    club_pending_invites = models.ManyToManyField('UserExt', related_name="pending_invites")