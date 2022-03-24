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
    path('club_chat/<int:club_id>/', views.club_chat, name="club_chat"),
    path('friend_list/<int:profile_id>/', views.friend_list, name='friend_list'),
    path('user_search_results/', views.user_search_results, name="user_search_results"),
    path('book_clubs/', views.book_clubs, name="book_clubs"),
    path('club_members/<int:club_id>/', views.club_members, name='club_members'),
    path('invite_to_club/<int:club_id>/', views.invite_to_club, name='invite_to_club'),
    path('view_book/<str:book_isbn>/', views.view_book, name='view_book'),
    path('search_book/', views.search_book, name="search_book"),
    path('club_library/<int:club_id>/', views.club_library, name="club_library"),
    path('create_club_post/<int:club_id>/', views.create_club_post, name="create_club_post"),
    path('create_profile_post/<int:profile_id>/', views.create_profile_post, name="create_profile_post"),
	path('reading_log/', views.reading_log, name='reading_log'),
    path('view_post/<int:post_id>/', views.view_post, name='view_post'),
    path('review_book/', views.create_review_post, name='create_review_post'),
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
    path('ajax/remove_from_library/<int:club_id>/<int:club_book_id>/', views.remove_from_library, name='remove_from_library'),
    path('ajax/add_to_library/<int:club_id>/<str:isbn>/', views.add_to_library, name='add_to_library'),
    path('ajax/dolike/<int:post_id>/', views.do_like, name="do_like"),
    path('ajax/make_comment/<int:post_id>/', views.make_comment, name="make_comment"),
    path('ajax/remove_from_user_library/<int:book_id>/', views.remove_from_user_library, name='remove_from_user_library'),
    path('ajax/add_to_user_library/<str:isbn>/', views.add_to_user_library, name='add_to_user_library'),
    ]
)