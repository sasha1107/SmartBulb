from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pathlib import Path
from accounts.models import CustomUser
from .models import Sentiment, Diary
import pandas as pd
import os

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
filename = os.path.join(BASE_DIR, 'diary', 'sentiment.csv')


def analyze_sentiment(text):
    return 0


def init_db(request):
    data = pd.read_csv(filename, encoding='utf-8')

    data = data['sentiment']

    for sent in data:
        sentiment = Sentiment()
        sentiment.sentiment = sent
        sentiment.save()

    return redirect('home')



@login_required
def save_diary(request):

    return render(request, "diary.html")


@login_required
def view_diary(request):
    return render(request, "diary.html")

