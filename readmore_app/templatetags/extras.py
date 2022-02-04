from django import template
from readmore_app.models import Notification, UserExt

register = template.Library()

@register.simple_tag
def num_notifications(user_id):
    try:
        this_user = UserExt.objects.get(pk=user_id)
        return Notification.objects.filter(notification_user=this_user).count()
    except Exception as e:
        return ""