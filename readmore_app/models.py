from django.db import models
from django.contrib.auth.models import User

# User model extension for adding more attributes
class UserExt(User):
    user_friends = models.ManyToManyField('UserExt', related_name="friends")
    user_birthdate = models.DateField()
    user_bio = models.TextField()
    user_interests = models.TextField()


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    notification_user = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    notification_title = models.CharField(max_length=10000)
    notification_time = models.DateTimeField()
    notification_link = models.CharField(max_length=10000, blank=True)
    notification_link_text = models.CharField(max_length=10000, blank=True)
    notification_message = models.TextField()
	
	
class Club(models.Model):
	club_id          = models.AutoField(primary_key=True)
	club_name        = models.CharField(max_length=100)
	club_description = models.TextField(blank=True, default="This is my book club.")
	club_owner       = models.ForeignKey(UserExt, on_delete=models.CASCADE)
	club_users       = models.ManyToManyField(UserExt, blank=True, related_name="users")