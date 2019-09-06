from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Activity(models.Model):
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class Task_Type(models.Model):
    image = models.ImageField()
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=150)
    create_layout = models.SlugField(unique=True, null=True)
    display_layout = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions', null=True)
    task_type = models.ForeignKey(Task_Type, on_delete=models.CASCADE, related_name='task_type', null=True)
    title = models.CharField(max_length=80)
    text = models.TextField(max_length=450)
    date = models.DateTimeField(auto_now_add=True)
    votes = GenericRelation(Activity, related_name='votes')
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
