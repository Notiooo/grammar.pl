from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.urls.base import reverse


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug_url = models.SlugField(unique=True)
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
    image = models.ImageField(blank=True)
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=150)
    slug_url = models.SlugField(null=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    task_type = models.ForeignKey(Task_Type, on_delete=models.CASCADE, related_name='task_type', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='task', null=True)
    title = models.CharField(max_length=80)
    text = models.TextField(max_length=450)
    votes = GenericRelation(Activity, related_name='votes')
    date = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('edit_task', kwargs={'pk': self.pk})

    def list_of_anwsers(self):
        "Gets all anwsers from queryset of questions"
        anwsers = []
        for question in self.question.all():
            for anwser in question.anwsers.all():
                anwsers.append(anwser)
        return anwsers


class Question(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='question', null=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text[:60] + "..."


class Anwser(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='anwsers')
    text = models.CharField(max_length=100, blank=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


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
