from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=80)
    text = models.TextField(max_length=450)
    date = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title

class Anwser(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='anwsers')
    anwser = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.anwser

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.comment