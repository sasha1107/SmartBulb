from django.db import models

# Create your models here.


class Diary(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateField('date published')
    body = models.TextField(default='')
    sentiment = models.CharField(choices=(("긍정", "긍정"), ("부정", "부정")), max_length=2, null=True, blank=True)

    def __str__(self):
        return self.title
