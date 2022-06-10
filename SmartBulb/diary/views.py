from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from pathlib import Path
from accounts.models import CustomUser
from .models import Sentiment, Diary
from .form import DiaryPost
import pandas as pd
from yeelight import discover_bulbs, Bulb
import random
import os
from .tree import *

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
filename = os.path.join(BASE_DIR, 'diary', 'sentiment.csv')
filename2 = os.path.join(BASE_DIR, 'diary', 'encouragement.csv')
bulb_request = False
bulb_on = 0
sentiment_to_light = {
    "긍정": [[0, 0, 255], [129, 193, 71]],
    "중립": [[255, 127, 0], [255, 0, 0]],
    "부정": [[255, 212, 0], [255, 212, 0]]
}


def analyze_sentiment(sentence):
    sentiment = Sentiment.objects.get(sentiment=get_sentiment(sentence))

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
    diary = Diary.objects.filter(user=request.user.id)
    dates = []

    for i in range(len(diary)):
        tmp = str(diary[i].pub_date.isoformat())
        tmp += "-" + str(diary[i].sentiment)
        # sentiment.append(diary[i].sentiment)
        dates.append(tmp)

    if not request.user.is_authenticated:
        return render(request, "main_diary.html", {"validity": 0})

    return render(request, "main_diary.html", {"diary": diary, "dates": dates})


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
    global bulb_request, bulb_on
    data = pd.read_csv(filename2, encoding='cp949')
    diary = Diary.objects.filter(user=request.user.id)
    diary_text = get_object_or_404(diary, pk=diary_id)

    data = data[f"{diary_text.sentiment}"]

    index = random.randint(0, 4)

    if bulb_request:
        bulb_request = False
        return render(request, "diary.html", {'diary': diary_text, "encourage": data[index], "sent" : str(diary_text.sentiment), 'bulb_on': bulb_on})
    else:
        return render(request, "diary.html", {'diary': diary_text, "encourage": data[index], "sent" : str(diary_text.sentiment)})


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


def statistics(request, year, month):
    diaries = Diary.objects.filter(user=request.user.id)

    sentiment_dict = {"긍정": 0, "부정": 0, "중립": 0}

    max_value = 0
    max_sentiment = ""

    if not diaries:
        return render(request, "statistics.html", {'sentiment_dict': 0})
    else:

        for diary in diaries:
            try:
                sentiment_dict[f"{diary.sentiment}"] += 1
            except Exception as err:
                sentiment_dict[f"{diary.sentiment}"] = 1

        for k, v in sentiment_dict.items():
            if max_value < v:
                max_value = v
                max_sentiment = k

        return render(request, "statistics.html", {'sentiment_dict': sentiment_dict, 'freq_sent': max_sentiment})


def turn_on_bulbs(request, diary_id):
    global bulb_request, bulb_on, sentiment_to_light

    # 수현 테스트 시작
    user = CustomUser.objects.get(username=request.user)
    bulb_ip = user.user_ip
    bulb_request = True

    if not bulb_ip:
        bulb_on = 0
        return redirect("view_diary", str(diary_id))
    else:
        diary = Diary.objects.filter(user=request.user.id)
        diary_text = get_object_or_404(diary, pk=diary_id)

        index = random.randint(0, 1)

        # 전구 연결
        bulb = Bulb(bulb_ip)

        # 전구가 꺼져 있을 때 켜기
        if bulb.get_properties()['power'] == 'off':
            bulb_on = 1
            bulb.turn_on()
        else:
            bulb_on = 1
        
        bulb.set_rgb(*(sentiment_to_light[f"{diary_text.sentiment}"][index]))  # sentiment 불러 오는 게 아직 안돼서 작동이 안 되는지 모르겠음
        # 수현 테스트 끝

        return redirect("view_diary", str(diary_id))
