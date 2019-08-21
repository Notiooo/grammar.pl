from django.contrib import admin
from . import models


class Matura_Anwser_Inline(admin.TabularInline):
    model = models.Matura_Anwser
    show_change_link = True


class Matura_Question_Inline(admin.TabularInline):
    model = models.Matura_Question
    show_change_link = True
    extra = 0


@admin.register(models.Matura_Task)
class MaturaTask(admin.ModelAdmin):
    inlines = [
        Matura_Question_Inline,
    ]


@admin.register(models.Matura_Question)
class MaturaQuestion(admin.ModelAdmin):
    readonly_fields = ['task']
    inlines = [
        Matura_Anwser_Inline,
    ]
