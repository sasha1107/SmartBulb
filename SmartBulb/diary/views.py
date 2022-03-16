from django.shortcuts import render

# Create your views here.


def analyze_sentiment(text):
    sentiment = "긍정"
    return sentiment


def save_diary(request):

    return render(request, "diary.html")
