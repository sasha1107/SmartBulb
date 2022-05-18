from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/register_bulb', views.register_bulb, name='register_bulb'),
]