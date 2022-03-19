from django.contrib import admin
from .models import Diary, Sentiment

# Register your models here.

admin.site.register(Diary)
admin.site.register(Sentiment)

