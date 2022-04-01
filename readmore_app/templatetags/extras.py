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

@register.simple_tag
def get_isbn_thirteen(identifiers):
    for id in identifiers:
        if id['type'] == "ISBN_13":
            return id['identifier']
    return None

@register.simple_tag
def get_isbn_ten(identifiers):
    for id in identifiers:
        if id['type'] == "ISBN_10":
            return id['identifier']
    return None

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def isbn_thirteen_filter(identifiers):
    for id in identifiers:
        if id['type'] == "ISBN_13":
            return id['identifier']
    return None