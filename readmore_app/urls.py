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
    path('create_club/', views.create_club, name='create_club'),
    path('club/<int:club_id>/', views.club, name='club'),
    path('friend_list/<int:profile_id>/', views.friend_list, name='friend_list'),
    path('search_results/', views.search_results, name="search_results"),
    path('book_clubs/', views.book_clubs, name="book_clubs"),
    path('club_members/<int:club_id>/', views.club_members, name='club_members'),
    path('invite_to_club/<int:club_id>/', views.invite_to_club, name='invite_to_club'),
]

# AJAX url patterns
urlpatterns.extend(
    [
    path('ajax/notifications/<int:notification_id>/', views.delete_notification, name="delete_notification"),
    path('ajax/friend/', views.process_friend, name='process_friend'),
    path('ajax/get_friend_count/<int:user_id>/', views.get_friend_count, name="get_friend_count"),
    path('ajax/leave_club/<int:club_id>/', views.leave_club, name="leave_club"),
    path('ajax/kick_member/<int:club_id>/<int:member_id>/', views.kick_member, name="kick_member"),
    path('ajax/invite_member/<int:club_id>/<int:friend_id>/', views.invite_member, name="invite_member"),
    path('ajax/join_club/<int:club_id>/', views.join_club, name="join_club"),
    ]
)