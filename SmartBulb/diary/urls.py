from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_diary, name='main_diary'),
    path('save_diary/<int:year>/<int:month>/<int:day>', views.save_diary, name='save_diary'),
    path('<int:diary_id>/', views.view_diary, name='view_diary'),
    path('<int:diary_id>/delete', views.delete_diary, name='delete_diary'),
    path('<int:diary_id>/edit', views.edit_diary, name='edit_diary'),
    path('statistics/<int:year>/<int:month>', views.statistics, name='statistics'),
]