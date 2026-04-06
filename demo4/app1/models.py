from django.contrib.auth.models import User
from django.db import models


class App1Data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.user.username})'


class App1Login(models.Model):
    user_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_id} | {self.username}'


