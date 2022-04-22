from django.contrib import admin
from .models import *

admin.site.register(UserExt)
admin.site.register(Notification)
admin.site.register(Club)
admin.site.register(ClubBook)
admin.site.register(ReadingLogBook)
admin.site.register(Chat)
admin.site.register(ClubChat)
admin.site.register(PM)
admin.site.register(Post)
admin.site.register(ClubPost)
admin.site.register(ProfilePost)
admin.site.register(ReviewPost)
admin.site.register(BookForumPost)
admin.site.register(Meeting)