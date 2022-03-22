from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from pathlib import Path
from accounts.models import CustomUser
from .models import Sentiment, Diary
from .form import DiaryPost
import pandas as pd
import os

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
filename = os.path.join(BASE_DIR, 'diary', 'sentiment.csv')


def analyze_sentiment(text):
    sentiment = Sentiment.objects.get(id=1)

    return sentiment


def init_db(request):
    data = pd.read_csv(filename, encoding='utf-8')

    data = data['sentiment']

    for sent in data:
        sentiment = Sentiment()
        sentiment.sentiment = sent
        sentiment.save()

    return redirect('home')


def main_diary(request):
    if not request.user.is_authenticated:
        return render(request, "main_diary.html", {"validity": 0})

    diary = Diary.objects.filter(user=request.user.id)

    return render(request, "main_diary.html", {'diaries': diary})


@login_required
def save_diary(request):
    user = CustomUser.objects.filter(username=str(request.user))
    if request.method == "POST":
        form = DiaryPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user[0]
            post.pub_date = timezone.now()
            post.sentiment = analyze_sentiment(post.text)
            post.save()
            return redirect("view_diary", str(post.id))
    else:
        form = DiaryPost()
        return render(request, "new.html", {'form': form})


@login_required
def view_diary(request, diary_id=1):
    diary = Diary.objects.filter(user=request.user.id)
    diary_text = get_object_or_404(diary, pk=diary_id)
    return render(request, "diary.html", {'diary': diary_text})

