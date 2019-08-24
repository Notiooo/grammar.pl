from django.db import models
from django.urls.base import reverse
from django.conf import settings
from .helpers import rename_sound_file
from .storage import OverwriteStorage
from datetime import datetime


# Create your models here.

class Matura_Task(models.Model):
    types = [
        ('audio', 'Rozumienie ze słuchu'),
        ('text', 'Rozumienie tekstów pisanych'),
        ('grammar', 'Znajomość środków językowych'),
    ]
    type = models.CharField(
        max_length=7,
        choices=types,
        default='audio',
    )
    layouts = [
        ('tnf', "Prawda i Fałsz"),
        ('letter', 'Dopasuj literę do osoby'),
        ('quiz', 'Quiz ABC'),
        ('reading-title', 'Dopasuj tytuł do tekstu'),
        ('image', 'Wybierz odpowiedź do obrazka'),
        ('fill-gap', 'Dopasuj odpowiedź do luki w tekście')
    ]
    layout = models.CharField(
        max_length=15,
        choices=layouts,
        default='tnf',
    )
    year = models.IntegerField(default=datetime.now().year)
    MONTHS = [
        ('MAJ', 'Maj'),
        ('CZE', 'Czerwiec'),
    ]
    month = models.CharField(
        max_length=3,
        choices=MONTHS,
        default='MAJ',
    )
    LEVELS = [
        ('roz', 'Rozszerzony'),
        ('pod', 'Podstawowy'),
        ('dwu', 'Dwujęzyczny'),
    ]
    level = models.CharField(
        max_length=3,
        choices=LEVELS,
        default='POD',
    )
    title = models.CharField(max_length=80)
    text = models.TextField(default="", blank=True)
    sound_file = models.FileField(blank=True, upload_to=rename_sound_file, storage=OverwriteStorage())
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.title + ' - ' + str(self.year) + ' ' + self.level

    def get_absolute_url(self):
        return reverse('matura_detail', kwargs={'pk': self.pk, 'year': self.year})


class Matura_Question(models.Model):
    task = models.ForeignKey(Matura_Task, on_delete=models.CASCADE, related_name='question')
    text = models.TextField()

    def __str__(self):
        return self.task.__str__()


class Matura_Anwser(models.Model):
    question = models.ForeignKey(Matura_Question, on_delete=models.CASCADE, related_name='anwser', null=True)
    text = models.CharField(max_length=150, blank=True, default="")
    correct_anwser = models.BooleanField(default=False)
