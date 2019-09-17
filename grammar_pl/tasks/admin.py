from django.contrib import admin
from . import models


# Register your models here.

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug_url': ('title',)}


@admin.register(models.Task_Type)
class TaskType(admin.ModelAdmin):
    prepopulated_fields = {'slug_url': ('title',)}

@admin.register(models.Anwser)
class Anwser(admin.ModelAdmin):
    pass

class AnwserInline(admin.TabularInline):
    model = models.Anwser

@admin.register(models.Question)
class Question(admin.ModelAdmin):
    inlines = [
        AnwserInline,
    ]

class QuestionInline(admin.TabularInline):
    show_change_link = True
    model = models.Question

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]

@admin.register(models.Votes)
class VotesAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Likes)
class LikesAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Comment)
class CommentsAdmin(admin.ModelAdmin):
    pass
