from django.contrib import admin
from django.utils.html import format_html
from django.urls.base import reverse
from django.shortcuts import redirect
from . import models


class Exams_Anwser_Inline(admin.TabularInline):
    model = models.Exams_Anwser
    extra = 4


class Exams_Question_Inline(admin.TabularInline):
    model = models.Exams_Question
    show_change_link = True
    extra = 0

class Exams_Task_Inline(admin.TabularInline):
    model = models.Exams_Task
    show_change_link = True
    extra = 0

@admin.register(models.Exams_Task)
class ExamsTask(admin.ModelAdmin):
    readonly_fields = ('category_link',)
    inlines = [
        Exams_Question_Inline,
    ]

    def response_change(self, request, obj):
        result = super(ExamsTask, self).response_change(request, obj)
        # it allows me to easily get redirected back to the page-view if I edited it from the page-view
        if "next" in request.GET:
            return redirect(request.GET['next'])
        return result

    def category_link(self, obj):
        url = reverse("admin:{}_{}_change".format(obj.category._meta.app_label, obj.category._meta.model_name),
                      args=(obj.category.id,))
        return format_html('<a href="{}">Edit the category</a>'.format(url))


@admin.register(models.Exams_Question)
class ExamsQuestion(admin.ModelAdmin):
    readonly_fields = ('task', 'task_link')

    def task_link(self, obj):
        url = reverse("admin:{}_{}_change".format(obj.task._meta.app_label, obj.task._meta.model_name),
                      args=(obj.task.id,))
        return format_html('<a href="{}">Edit the task</a>'.format(url))

    inlines = [
        Exams_Anwser_Inline,
    ]
@admin.register(models.Exams_Category)
class ExamsCategory(admin.ModelAdmin):
    ordering = ('-year',)
    prepopulated_fields = {'slug_url': ('year', 'type', 'month', 'level',)}
    inlines = [
        Exams_Task_Inline,
    ]