from django.contrib import admin
from . import models

# Register your models here.

class Matura_Anwser_Inline(admin.TabularInline):
    model = models.Matura_Anwser

@admin.register(models.Matura_Task)
class MaturaTask(admin.ModelAdmin):
    inlines = [
        Matura_Anwser_Inline,
    ]
