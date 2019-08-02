from django.db import models
from django.urls.base import reverse
from django.conf import settings


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
    year = models.IntegerField(null=True)
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
        ('ROZ', 'Rozszerzony'),
        ('POD', 'Podstawowy'),
        ('DWU', 'Dwujęzyczny'),
    ]
    level = models.CharField(
        max_length=3,
        choices=LEVELS,
        default='POD',
    )
    title = models.CharField(max_length=80)
    text = models.TextField()
    sound_file = models.FileField(blank=True)
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.title + ' - ' + str(self.year) + ' ' + self.level

    def get_absolute_url(self):
        return reverse('matura_detail', args=[str(self.id)])


class Matura_Anwser(models.Model):
    task = models.ForeignKey(Matura_Task, on_delete=models.CASCADE, related_name='anwser')
    text = models.CharField(max_length=150)
    correct_anwser = models.BooleanField(default=False)
