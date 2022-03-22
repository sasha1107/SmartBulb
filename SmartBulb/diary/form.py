from django import forms
from .models import Diary


class DiaryPost(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['title', 'text']

