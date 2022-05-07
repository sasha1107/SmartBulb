from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from accounts.models import CustomUser


# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html", {"validity": 1, "username": request.user})
    else:
        return render(request, "home.html", {"validity": 0})

