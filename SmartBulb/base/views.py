from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth


# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html", {"validity": 1})
    else:
        return render(request, "home.html", {"validity": 0})
