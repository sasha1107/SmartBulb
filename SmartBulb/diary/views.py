from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from pathlib import Path
from accounts.models import CustomUser
from .models import Sentiment, Diary
from .form import DiaryPost
import pandas as pd
from soynlp.normalizer import *
from hanspell import spell_checker
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertModel
from kobert.utils import get_tokenizer
from transformers import BertModel
import os

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
filename = os.path.join(BASE_DIR, 'diary', 'sentiment.csv')
batch_size = 64
max_len = 64
bModelLoaded = False


class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size=768,
                 num_classes=4,  ##클래스 수 조정##
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size, num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        _, pooler = self.bert(input_ids=token_ids, token_type_ids=segment_ids.long(),
                              attention_mask=attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        return self.classifier(out)


class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len,
                 pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))


if not bModelLoaded:
    tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
    vocab = nlp.vocab.BERTVocab.from_sentencepiece(tokenizer.vocab_file, padding_token='[PAD]')
    bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
    tokenizer = get_tokenizer()
    tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
    device = torch.device("cuda:0")
    model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)
    model.load_state_dict(torch.load(os.path.join(BASE_DIR, 'diary', 'model2.pth')))
    bModelLoaded = True


def emotion_to_word(sentence):
    sentence.replace('ㅠㅠ', '우는 얼굴')
    sentence.replace('ㅜㅜ', '우는 얼굴')
    sentence.replace('ㅡㅡ', '짜증난 얼굴')
    sentence.replace('ㅎㅎ', '웃음')
    sentence.replace('ㅋㅋ', '웃음')
    sentence.replace('^^', '웃는 얼굴')
    return sentence


def analyze_sentiment(sentence):
    sentiment = Sentiment()
    emotion_norm = emoticon_normalize(sentence, num_repeats=2)
    emotion_sentence = emotion_to_word(sentence)
    predict_sentence = spell_checker.check(emotion_sentence).checked
    data = [predict_sentence, '0']
    dataset_another = [data]

    another_test = BERTDataset(dataset_another, 0, 1, tok, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=0)

    model.eval()

    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length = valid_length
        label = label.long().to(device)
        out = model(token_ids, valid_length, segment_ids)
        test_eval = []
        for i in out:
            logits = i
            logits = logits.detach().cpu().numpy()

            if np.argmax(logits) == 0:
                test_eval.append("행복")
            elif np.argmax(logits) == 1:
                test_eval.append("분노")
            elif np.argmax(logits) == 2:
                test_eval.append("슬픔")
            elif np.argmax(logits) == 3:
                test_eval.append("중립")

    sentiment.sentiment = test_eval[0]
    sentiment.save()

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


