from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from pathlib import Path
from accounts.models import CustomUser
from .models import Sentiment, Diary
from .form import DiaryPost
import pandas as pd
# from soynlp.normalizer import *
# from hanspell import spell_checker
import os

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
filename = os.path.join(BASE_DIR, 'diary', 'sentiment.csv')


def analyze_sentiment(sentence):
    sentiment = Sentiment.objects.get(sentiment="중립")

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

    return render(request, "main_diary.html")


@login_required
def save_diary(request, year, month, day):
    diaries = Diary.objects.filter(user=request.user.id)
    user = CustomUser.objects.filter(username=str(request.user))
    date_time_str = str(year) + '-' + str(month) + '-' + str(day)
    date_time_str = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

    if diaries is not None:
        for diary in diaries:
            i = 0
            pub_date_converted = str(diary.pub_date)
            date_time_str = str(date_time_str)
            date_time_str = date_time_str[:len(pub_date_converted)]

            if pub_date_converted == date_time_str:
                return redirect("view_diary", str(diary.id))

    if request.method == "POST":
        form = DiaryPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user[0]
            post.pub_date = date_time_str
            post.sentiment = analyze_sentiment(post.text)
            post.save()
            return redirect("view_diary", str(post.id))
    else:
        form = DiaryPost()
        return render(request, "new.html", {'form': form, 'year': year, 'month': month, 'day': day})


@login_required
def view_diary(request, diary_id):
    diary = Diary.objects.filter(user=request.user.id)
    diary_text = get_object_or_404(diary, pk=diary_id)
    return render(request, "diary.html", {'diary': diary_text})


@login_required
def delete_diary(request, diary_id):
    diary = Diary.objects.filter(user=request.user.id)
    diary_text = get_object_or_404(diary, pk=diary_id)
    diary_text.delete()
    return redirect("main_diary")


@login_required
def edit_diary(request, diary_id):
    diary = Diary.objects.filter(user=request.user.id)
    diary_text = get_object_or_404(diary, pk=diary_id)

    if request.method == "POST":
        form = DiaryPost(request.POST)
        if form.is_valid():
            diary_text.title = form.cleaned_data['title']
            diary_text.text = form.cleaned_data['text']
            diary_text.sentiment = analyze_sentiment(diary_text.text)
            diary_text.save()
            return redirect("view_diary", str(diary_text.id))
    else:
        form = DiaryPost(instance=diary_text)
        context = {
            'form': form,
            'writing': True,
            'now': 'edit',
            'diary': diary_text,
        }
        return render(request, "edit.html", context)


