from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class CustomUser(User):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)