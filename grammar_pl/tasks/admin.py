from django.contrib import admin
from . import models


# Register your models here.

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.Task_Type)
class TaskTypeAdmin(admin.ModelAdmin):
    pass


class CommentInline(admin.TabularInline):
    model = models.Comment


class AnwserInline(admin.TabularInline):
    model = models.Anwser


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
        AnwserInline,
    ]


admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Comment)
