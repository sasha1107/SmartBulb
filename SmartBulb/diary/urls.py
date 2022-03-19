from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('save_diary/', views.save_diary, name='save_diary'),
    path('view_diary/', views.view_diary, name='view_diary'),
]