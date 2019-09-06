from django.db import models
from django.urls.base import reverse
from django.conf import settings
from .helpers import rename_sound_file, rename_exam_file, rename_exam_anwser_file, rename_image_file
from .storage import OverwriteStorage
from datetime import datetime


# Create your models here.

class Exams_Category(models.Model):
    TYPES = [
        ('matura', 'Matura'),
        ('osmioklasisty', 'Egzamin Ośmioklasisty'),
        ('gimnazjalny', 'Egzamin Gimnazjalny'),
    ]
    LEVELS = [
        ('pod', 'Podstawowy'),
        ('roz', 'Rozszerzony'),
        ('dwu', 'Dwujęzyczny'),
        (None, '---'),
    ]
    MONTHS = [
        ('MAJ', 'Maj'),
        ('CZE', 'Czerwiec'),
        ('KWI', 'Kwiecień'),
        (None, '---'),
    ]

    year = models.IntegerField(default=datetime.now().year)
    level = models.CharField(
        max_length=3,
        choices=LEVELS,
        default=None,
    )
    month = models.CharField(
        max_length=3,
        choices=MONTHS,
        default=None,
    )
    type = models.CharField(
        max_length=16,
        choices=TYPES,
        default='matura',
    )
    slug_url = models.SlugField(unique=True)
    exam_file = models.FileField(blank=True, upload_to=rename_exam_file, storage=OverwriteStorage())
    exam_anwsers_file = models.FileField(blank=True, upload_to=rename_exam_anwser_file, storage=OverwriteStorage())

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.get_type_display(), self.year, self.get_level_display(),
                                        self.get_month_display())

    @staticmethod
    def get_task_types():
        return Exams_Task.types

    @staticmethod
    def get_category_types():
        return Exams_Category.TYPES


class Exams_Task(models.Model):
    category = models.ForeignKey(Exams_Category, on_delete=models.CASCADE, related_name='task', null=True)
    types = [
        ('listening', 'Rozumienie ze słuchu'),
        ('reading', 'Rozumienie tekstów pisanych'),
        ('grammar', 'Znajomość środków językowych'),
    ]
    type = models.CharField(
        max_length=10,
        choices=types,
        default='listening',
    )
    layouts = [
        ('tnf', "Prawda i Fałsz"),
        ('letter', 'Dopasuj literę do osoby'),
        ('quiz', 'Quiz ABC'),
        ('reading-title', 'Dopasuj tytuł do tekstu'),
        ('reading-table', 'Dopasuj zdanie do tekstu/litery (tabela)'),
        ('fill-gap-letter', 'Dopasuj literę do luki w tekście'),
        ('fill-gap', 'Dopasuj słowo/zdanie do luki w tekście')
    ]
    layout = models.CharField(
        max_length=15,
        choices=layouts,
        default='tnf',
    )
    title = models.CharField(max_length=100)
    text = models.TextField(default="", blank=True)
    sound_file = models.FileField(blank=True, upload_to=rename_sound_file, storage=OverwriteStorage())
    image = models.ImageField(blank=True, upload_to=rename_image_file, storage=OverwriteStorage())

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('exams_detail',
                       kwargs={'pk': self.pk, 'year': self.get_year(), 'exam_category': self.category.type})

    def text_fill_blank_list_split(self):
        return self.text.split('_')

    def list_of_anwsers(self):
        "Gets all anwsers from queryset of questions"
        anwsers = []
        for question in self.question.all():
            for anwser in question.anwser.all():
                anwsers.append(anwser)
        return anwsers

    def get_year(self):
        return self.category.year

    def get_level(self):
        return self.category.level

    def get_level_display(self):
        return self.category.get_level_display()


class Exams_Question(models.Model):
    task = models.ForeignKey(Exams_Task, on_delete=models.CASCADE, related_name='question')
    text = models.TextField(default="", blank=True)

    def __str__(self):
        return self.task.__str__()

    def get_anwsers_text_list(self):
        anwsers = [question.text for question in self.anwser.all()]
        return anwsers

    def get_anwsers_boolean_list(self):
        anwsers = [question.correct_anwser for question in self.anwser.all()]
        return anwsers

    def slice_questions(self):
        return self.text.split('/')


class Exams_Anwser(models.Model):
    question = models.ForeignKey(Exams_Question, on_delete=models.CASCADE, related_name='anwser', null=True)
    text = models.CharField(max_length=150, blank=True, default="")
    correct_anwser = models.BooleanField(default=False)

    def slice_anwsers(self):
        return self.text.split('/')

    def __str__(self):
        return self.question.text[:80] + "..."
