from django.db import models
from django.contrib.auth.models import User

# User model extension for adding more attributes
class UserExt(User):
    user_friends = models.ManyToManyField('UserExt', related_name="friends")
    user_birthdate = models.DateField()
    user_bio = models.TextField()
    user_interests = models.TextField()


    