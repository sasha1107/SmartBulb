"""SmartBulb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.urls import include
import accounts.views
import base.views
import diary.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', base.views.home, name='home'),
    path('signup/', accounts.views.signup, name='signup'),
    path('login/', accounts.views.login, name='login'),
    path('logout/', accounts.views.logout, name='logout'),
    path('save_diary/', diary.views.save_diary, name='save_diary'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]