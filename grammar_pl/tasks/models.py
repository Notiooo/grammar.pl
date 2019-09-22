from django.db import models
from django.conf import settings
from django.urls.base import reverse


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug_url = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_public_tasks(self):
        return self.task.all().filter(public=True).order_by('-pk')


class Task_Type(models.Model):
    image = models.ImageField(blank=True)
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=150)
    slug_url = models.SlugField(null=True)
    layout_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    task_type = models.ForeignKey(Task_Type, on_delete=models.CASCADE, related_name='task_type', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='task', null=True)
    title = models.CharField(max_length=80)
    text = models.TextField(max_length=450, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    source = models.CharField(max_length=150, blank=True)
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

    def get_upvotes(self):
        return self.votes.filter(activity_type=Votes.UP_VOTE).count()

    def get_downvotes(self):
        return self.votes.filter(activity_type=Votes.DOWN_VOTE).count()

    def get_sum_votes(self):
        return self.get_upvotes() - self.get_downvotes()


class Question(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='question', null=True)
    text = models.CharField(max_length=200)
    explanation = models.CharField(max_length=180, blank=True)

    def __str__(self):
        return self.text[:60] + "..."


class Anwser(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='anwsers')
    text = models.CharField(max_length=100, blank=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', null=True)
    text = models.TextField(max_length=300, default="")
    date = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text


class Votes(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='votes', null=True)
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (UP_VOTE, 'upvote'),
        (DOWN_VOTE, 'downvote'),
    )
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('task', 'user')

    def get_upvotes(self):
        return self.objects.filter(activity_type=self.UP_VOTE).count()

    def get_downvotes(self):
        return self.objects.filter(activity_type=self.DOWN_VOTE).count()

    def get_sum_votes(self):
        return self.get_upvotes() - self.get_upvotes()


class Likes(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    class Meta:
        unique_together = ('comment', 'user')

class Favourites(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='favourites', null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    class Meta:
        unique_together = ('task', 'user')