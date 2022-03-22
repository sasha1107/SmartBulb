from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_diary, name='main_diary'),
    path('save_diary/', views.save_diary, name='save_diary'),
    path('<int:diary_id>/', views.view_diary, name='view_diary'),
]