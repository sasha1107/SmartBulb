from django.db import models

# Create your models here.


class Sentiment(models.Model):
    sentiment = models.CharField(default='', max_length=10)

    def __str__(self):
        return self.sentiment


class Diary(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateField('date published')
    body = models.TextField(default='')
    sentiment = models.ForeignKey(Sentiment, on_delete=models.CASCADE, blank=True, null=True, related_name='sent')

    def __str__(self):
        return self.title


