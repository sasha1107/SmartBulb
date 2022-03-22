from django.db import models
from accounts.models import CustomUser

# Create your models here.


class Sentiment(models.Model):
    sentiment = models.CharField(default='', max_length=10)

    def __str__(self):
        return self.sentiment


class Diary(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateField('작성일')
    text = models.TextField(default='')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='user')
    sentiment = models.ForeignKey(Sentiment, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title


