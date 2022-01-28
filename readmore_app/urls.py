from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('login/<int:account_created>/', views.login, name='login_account_created'),
    path('logout/', views.logout, name='logout'),
]