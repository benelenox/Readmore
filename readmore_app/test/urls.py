from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('login/<int:account_created>/', views.login, name='login_account_created'),
    path('logout/', views.logout, name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/<int:profile_id>/', views.profile, name='profile'),
    path('ajax/notifications/<int:notification_id>/', views.delete_notification, name="delete_notification"),
    path('ajax/friend/', views.process_friend, name='process_friend'),
]